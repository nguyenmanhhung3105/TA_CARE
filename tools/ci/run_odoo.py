#!/usr/bin/env python3
"""Build pinned CI runtime; test only disposable, networkless Docker resources."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]
MODULES = 'tacare_account_access,tacare_website'


def extract(raw, destination, strip_prefix=False):
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or not (member.isdir() or member.isfile()):
                raise ValueError('Unsafe CI source archive')
            parts = path.parts[1:] if strip_prefix else path.parts
            if not parts:
                continue
            target = destination.joinpath(*parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output)
                target.chmod(0o755 if member.mode & 0o111 else 0o644)
    destination.chmod(0o755)
    for directory in destination.rglob('*'):
        if directory.is_dir():
            directory.chmod(0o755)


def baseline_sha(value):
    if not value or value == '0' * 40:
        result = subprocess.run(['git', 'rev-parse', '--verify', 'refs/remotes/origin/main'], cwd=ROOT,
                                capture_output=True, text=True)
        if result.returncode:
            raise ValueError('An existing baseline commit is required; pass --baseline-sha')
        value = result.stdout.strip()
    if not re.fullmatch('[0-9a-f]{40}', value):
        raise ValueError('Invalid CI baseline SHA')
    subprocess.run(['git', 'cat-file', '-e', value + ':source/apps/tacare/addons'], cwd=ROOT,
                   check=True, capture_output=True)
    return value


def config(database, addons='/mnt/addons'):
    if database not in ('tacare_ci', 'tacare_ci_upgrade') or addons not in ('/mnt/addons', '/mnt/baseline'):
        raise ValueError('Only disposable CI databases/addons are allowed')
    return f'''[options]
db_host = /ci-socket
db_port = 5432
db_user = odoo_ci
db_name = {database}
dbfilter = ^{database}$
list_db = False
addons_path = /opt/odoo/odoo-server/addons,{addons}
data_dir = /var/lib/odoo
http_interface = 127.0.0.1
http_port = 8069
workers = 0
max_cron_threads = 0
proxy_mode = True
log_level = warn
without_demo = True
'''


def run(args):
    os.umask(0o077)
    pins = json.loads((ROOT / 'tools/ci/runtime.json').read_text())
    baseline = baseline_sha(args.baseline_sha)
    runtime = Path(args.runtime).resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    reports = runtime / 'reports'
    reports.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='run-', dir=runtime))
    # Mounted source must be traversable by the unprivileged container user.
    work.chmod(0o755)
    identifier = 'tacare-ci-' + uuid.uuid4().hex[:12]
    pg, app, socket, data, evidence = (identifier + suffix for suffix in ('-pg', '-app', '-socket', '-data', '-reports'))
    volumes, containers = [], []
    stages = []
    current = 'prepare'

    def command(arguments, content=None, timeout=1500, check=True, capture=True, log_output=True):
        with (work / (current + '.private.log')).open('ab') as log:
            result = subprocess.run([str(a) for a in arguments], input=content,
                                    stdout=subprocess.PIPE if capture else log,
                                    stderr=subprocess.PIPE if capture else log, timeout=timeout)
            if capture and log_output:
                log.write(result.stdout)
                log.write(result.stderr)
        if check and result.returncode:
            raise RuntimeError('CI step failed; raw diagnostics remain in the local private runtime directory')
        return result

    def docker(*arguments, **kwargs):
        return command(['docker', *arguments], **kwargs)

    def stage(name):
        nonlocal current
        current = name
        stages.append(name)
        print('[CI] ' + name, flush=True)

    def odoo(database, *arguments, addons='/mnt/addons', script=None):
        configuration = '/var/lib/odoo/' + database + '.conf'
        docker('exec', '-i', app, 'sh', '-c', 'cat > ' + configuration,
               content=config(database, addons).encode())
        return docker('exec', '-i', app, '/opt/venv/bin/python', '/opt/odoo/odoo-server/odoo-bin',
                      *arguments, '-c', configuration, '-d', database, content=script)

    def shell(database, name, addons='/mnt/addons'):
        return odoo(database, 'shell', '--no-http', addons=addons,
                    script=f"exec(compile(open('/ci/{name}').read(), '/ci/{name}', 'exec'))\n".encode())

    def terminate(signum, frame):
        raise InterruptedError('CI interrupted')

    previous_handlers = {sig: signal.signal(sig, terminate) for sig in (signal.SIGTERM, signal.SIGINT)}
    success = False
    try:
        stage('pinned-runtime')
        if args.archive:
            archive = Path(args.archive).read_bytes()
        else:
            url = 'https://codeload.github.com/odoo/odoo/tar.gz/' + pins['odoo_commit']
            with urllib.request.urlopen(url, timeout=180) as response:
                archive = response.read()
        if hashlib.sha256(archive).hexdigest() != pins['odoo_archive_sha256']:
            raise ValueError('Odoo source checksum mismatch')
        core = work / 'core'
        extract(archive, core, strip_prefix=True)
        old = work / 'baseline'
        raw = command(['git', '-C', ROOT, 'archive', baseline + ':source/apps/tacare/addons'], log_output=False).stdout
        extract(raw, old)
        build = work / 'build'
        build.mkdir()
        for name in ('Dockerfile', 'package.json', 'package-lock.json'):
            shutil.copyfile(ROOT / 'tools/ci' / name, build / name)
        shutil.copyfile(core / 'requirements.txt', build / 'requirements.txt')
        image = 'tacare-ci:' + hashlib.sha256(b''.join(p.read_bytes() for p in sorted(build.iterdir()))).hexdigest()[:16]
        docker('build', '--build-arg', 'PLAYWRIGHT_IMAGE=' + pins['playwright_image'], '-t', image, build, capture=False)

        stage('isolated-postgresql')
        for volume in (socket, data, evidence):
            docker('volume', 'create', '--label', 'tacare.ci=' + identifier, volume)
            volumes.append(volume)
        mounts = ['-v', socket + ':/ci-socket', '-v', data + ':/var/lib/odoo', '-v', evidence + ':/reports']
        docker('run', '--rm', '--network', 'none', '--user', 'root', *mounts,
               '--entrypoint', 'chmod', pins['postgres_image'], '0777', '/ci-socket', '/var/lib/odoo', '/reports')
        containers.append(pg)
        docker('run', '-d', '--name', pg, '--label', 'tacare.ci=' + identifier, '--network', 'none',
               '--memory', '512m', '--tmpfs', '/var/lib/postgresql/data',
               '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', '-v', socket + ':/ci-socket',
               pins['postgres_image'], '-c', 'listen_addresses=', '-c', 'max_connections=30',
               '-c', 'shared_buffers=64MB', '-c', 'max_locks_per_transaction=1024',
               '-c', 'unix_socket_directories=/var/run/postgresql,/ci-socket', '-c', 'unix_socket_permissions=0777')
        for attempt in range(90):
            result = docker('exec', '--user', 'postgres', pg, 'pg_isready', '-h', '/ci-socket', '-U', 'postgres', check=False)
            if result.returncode == 0 and b'PostgreSQL init process complete' in docker('logs', pg).stdout:
                break
            time.sleep(1)
        else:
            raise RuntimeError('Disposable PostgreSQL did not become ready')
        docker('exec', '-i', '--user', 'postgres', pg, 'psql', '-X', '-v', 'ON_ERROR_STOP=1',
               '-h', '/ci-socket', '-U', 'postgres', '-d', 'postgres', content=(
                   'CREATE ROLE odoo_ci LOGIN CREATEDB;\n'
                   'CREATE DATABASE tacare_ci OWNER odoo_ci;\n'
                   'CREATE DATABASE tacare_ci_upgrade OWNER odoo_ci;\n').encode())
        containers.append(app)
        docker('run', '-d', '--name', app, '--label', 'tacare.ci=' + identifier, '--network', 'none',
               '--memory', '3g', '--shm-size', '1g', *mounts,
               '--add-host', 'khovieclam.localhost:127.0.0.1',
               '--add-host', 'tuhoso.localhost:127.0.0.1', '--add-host', 'tacare.localhost:127.0.0.1',
               '-v', str(core) + ':/opt/odoo/odoo-server:ro',
               '-v', str(ROOT / 'source/apps/tacare/addons') + ':/mnt/addons:ro',
               '-v', str(old) + ':/mnt/baseline:ro', '-v', str(ROOT / 'tools/ci') + ':/ci:ro',
               '--entrypoint', 'sleep', image, 'infinity')

        stage('clean-install')
        odoo('tacare_ci', '-i', MODULES, '--without-demo=True', '--stop-after-init', '--no-http')
        shell('tacare_ci', 'fixture.py')
        shell('tacare_ci', 'native_checks.py')

        stage('upgrade-existing-records')
        odoo('tacare_ci_upgrade', '-i', MODULES, '--without-demo=True', '--stop-after-init', '--no-http', addons='/mnt/baseline')
        shell('tacare_ci_upgrade', 'fixture.py', addons='/mnt/baseline')
        odoo('tacare_ci_upgrade', '-u', MODULES, '--stop-after-init', '--no-http')
        shell('tacare_ci_upgrade', 'native_checks.py')

        stage('native-http-browser')
        docker('exec', '-d', app, '/opt/venv/bin/python', '/opt/odoo/odoo-server/odoo-bin',
               '-c', '/var/lib/odoo/tacare_ci.conf', '-d', 'tacare_ci',
               '--logfile', '/var/lib/odoo/http.private.log')
        docker('exec', app, 'node', '/ci/browser.cjs', timeout=600)
        success = True
    finally:
        # Ignore another termination signal while deleting only this run's named resources.
        for sig in previous_handlers:
            signal.signal(sig, signal.SIG_IGN)
        cleanup_complete = True
        evidence_copied = False
        if app in containers:
            try:
                evidence_copied = docker('cp', app + ':/reports/.', str(reports), timeout=60, check=False).returncode == 0
            except subprocess.SubprocessError:
                pass
        for container in reversed(containers):
            try:
                cleanup_complete &= docker('rm', '-f', container, timeout=60, check=False).returncode == 0
            except subprocess.SubprocessError:
                cleanup_complete = False
        for volume in reversed(volumes):
            try:
                cleanup_complete &= docker('volume', 'rm', volume, timeout=60, check=False).returncode == 0
            except subprocess.SubprocessError:
                cleanup_complete = False
        (reports / 'summary.json').write_text(json.dumps({
            'passed': success and cleanup_complete and evidence_copied, 'stages': stages, 'baseline_commit': baseline,
            'odoo_commit': pins['odoo_commit'], 'disposable_resources_cleaned': cleanup_complete,
        }, indent=2) + '\n')
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
    if not cleanup_complete or not evidence_copied:
        raise RuntimeError('CI evidence collection or disposable resource cleanup failed')
    print('PASS CI: clean install, baseline upgrade, native security/work reviews, browser and cleanup', flush=True)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', default=os.environ.get('CI_RUNTIME', str(ROOT / 'runtime/ci')))
    parser.add_argument('--baseline-sha', default=os.environ.get('CI_BASELINE_SHA', ''))
    parser.add_argument('--archive', type=Path, help='Optional predownloaded archive; checksum is still required')
    try:
        raise SystemExit(run(parser.parse_args()))
    except (ValueError, RuntimeError, InterruptedError, subprocess.SubprocessError) as error:
        print('FAIL CI: ' + str(error), flush=True)
        raise SystemExit(1)
