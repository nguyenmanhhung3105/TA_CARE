"""Offline regression tests: no production access or real remote push."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SERVER = ROOT / 'tools/deploy/server'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


installer = module('installer', SERVER / 'install_modes.py')
gate = module('gate', SERVER / 'data_bundle.py')
release = module('release', ROOT / 'tools/deploy/release.py')
transfer = module('transfer', ROOT / 'source/apps/tacare/addons/tacare_website/tools/data_transfer.py')


class PatchTests(unittest.TestCase):
    def test_worker_patch_stays_inside_staging_and_rollback(self):
        before = (Path(__file__).parent / 'worker_contract_fixture.sh').read_text()
        extension = (SERVER / 'worker_extension.sh').read_text()
        after = installer.patch_worker(before, extension)
        installer.validate_worker(after)
        self.assertEqual(installer.patch_worker(after, extension), after)
        self.assertIn('tacare-live-$GATE_ID-data-import.service', after)
        self.assertIn('tacare-stage-$GATE_ID-data-import.service', after)
        self.assertIn('"data_sha=$DATA_SHA"', after)
        for changed in (before.replace('    SHA=$1', '    SHA=${1}'), before.replace('    start_probe stage', '    custom_probe stage')):
            with self.assertRaises(ValueError):
                installer.patch_worker(changed, extension)

    def test_wrapper_rejects_bad_arguments_before_systemd(self):
        # Safely run the real wrapper with the EUID guard removed, and a fake
        # systemd-run. Its final worker command is recorded, never executed.
        raw = (SERVER / 'deploy.sh').read_text()
        raw = '\n'.join(line for line in raw.splitlines() if not line.startswith('[[ $EUID'))
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'systemd-run'
            fake.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@"\n')
            fake.chmod(0o755)
            environment = {**os.environ, 'PATH': directory + ':' + os.environ['PATH']}
            for args, success in [(['a' * 40], True), (['a' * 40, '--with-data', 'b' * 64], True),
                                  (['a' * 40, '--with-data', '../file'], False),
                                  (['a' * 40, '--with-data', 'b' * 64, 'extra'], False),
                                  (['a' * 40, '--unknown', 'b' * 64], False), (['bad'], False)]:
                result = subprocess.run(['bash', '-c', raw, 'wrapper', *args], env=environment, capture_output=True, text=True)
                self.assertEqual(result.returncode == 0, success)
                if success:
                    self.assertIn('/usr/local/lib/tacare-deploy/worker.sh', result.stdout)

    def test_code_mode_never_calls_data_import(self):
        raw = 'set -Eeuo pipefail\n' + (SERVER / 'worker_extension.sh').read_text()
        result = subprocess.run(['bash', '-c', raw + '\nrun_data_import stage missing\necho CODE_ONLY_OK\n'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'CODE_ONLY_OK')

    def test_stage_import_failure_stops_the_worker(self):
        # Real extension, fake transport preparation and staging service.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'app').mkdir()
            (root / 'data_bundle.py').write_text(
                'from pathlib import Path\nimport sys\np=Path(sys.argv[3]); (p/"import-command.py").write_text("pass\\n")\n')
            raw = 'set -Eeuo pipefail\n' + (SERVER / 'worker_extension.sh').read_text()
            raw += f'\nROOT={shlex.quote(directory)}\nWORK={shlex.quote(directory)}\nDATA_SHA={"b" * 64}\nDB=tacare_prod\n'
            raw += 'log() { :; }\nrun_stage() { cat >/dev/null; return 17; }\n'
            raw += 'run_data_import stage unused\necho SHOULD_NOT_ENTER_PRODUCTION\n'
            result = subprocess.run(['bash', '-c', raw], capture_output=True, text=True)
            self.assertEqual(result.returncode, 17, result.stderr)
            self.assertNotIn('SHOULD_NOT_ENTER_PRODUCTION', result.stdout)


class BundleTests(unittest.TestCase):
    def test_hash_json_and_size_validation(self):
        raw = json.dumps({'format': transfer.FORMAT, 'accounts': [{}], 'records': [{}]}).encode()
        key = hashlib.sha256(raw).hexdigest()
        self.assertEqual(gate.verify(raw, key)['accounts'], 1)
        for content, checksum in [(raw, 'a' * 64), (raw, '../file'),
                                  (b'{"format":1,"format":2}', hashlib.sha256(b'{"format":1,"format":2}').hexdigest())]:
            with self.assertRaises(ValueError):
                gate.verify(content, checksum)
        with patch.object(gate, 'MAX_BYTES', 1), self.assertRaises(ValueError):
            gate.verify(raw, key)

    def test_private_file_and_symlink_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'data.json'
            source.write_bytes(b'private')
            source.chmod(0o600)
            self.assertEqual(gate.read_file(source), b'private')
            source.chmod(0o644)
            with self.assertRaises(ValueError):
                gate.read_file(source)
            source.chmod(0o600)
            link = Path(directory) / 'link'
            link.symlink_to(source)
            with self.assertRaises(OSError):
                gate.read_file(link)


def workflow_scripts():
    lines = (ROOT / '.github/workflows/deploy-tacare.yml').read_text().splitlines(True)
    scripts = []
    for i, line in enumerate(lines):
        if line == '        run: |\n':
            block = []
            for following in lines[i + 1:]:
                if following.strip() and not following.startswith('          '):
                    break
                block.append(following[10:] if following.startswith('          ') else following)
            scripts.append(''.join(block))
    return scripts


class WorkflowTests(unittest.TestCase):
    def selection(self, event, message='', mode='', data=''):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'output'
            output.touch()
            environment = {**os.environ, 'EVENT_NAME': event, 'HEAD_MESSAGE': message,
                           'REQUESTED_MODE': mode, 'REQUESTED_DATA': data, 'GITHUB_OUTPUT': str(output)}
            result = subprocess.run(['bash', '-c', workflow_scripts()[0]], env=environment, capture_output=True, text=True)
            return result.returncode, output.read_text()

    def test_selection_and_safe_inputs(self):
        key = 'b' * 64
        self.assertEqual(self.selection('push'), (0, 'mode=code\ndata=\n'))
        self.assertEqual(self.selection('push', 'Release\n\nTacare-Data-SHA256: ' + key),
                         (0, 'mode=with-data\ndata=' + key + '\n'))
        self.assertEqual(self.selection('workflow_dispatch', mode='with-data', data=key)[0], 0)
        self.assertEqual(self.selection('workflow_dispatch', mode='code')[0], 0)
        for args in [('push', 'Tacare-Data-SHA256: x'),
                     ('push', f'Tacare-Data-SHA256: {key}\nTacare-Data-SHA256: {key}'),
                     ('workflow_dispatch', '', 'with-data', '$(touch /tmp/should-not-run)'),
                     ('workflow_dispatch', '', 'code', key), ('workflow_dispatch', '', 'unknown', '')]:
            self.assertNotEqual(self.selection(*args)[0], 0)
        for script in workflow_scripts():
            subprocess.run(['bash', '-n'], input=script.encode(), check=True)


class ReleaseTests(unittest.TestCase):
    def test_each_release_has_its_own_mode_and_never_stages_code(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / 'repo'
            remote = Path(directory) / 'remote.git'
            def run(*args):
                return subprocess.run(['git', *args], cwd=work, check=True, text=True, capture_output=True).stdout.strip()
            subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
            work.mkdir()
            run('init', '-b', 'main')
            run('config', 'user.name', 'Local release QA')
            run('config', 'user.email', 'qa@example.invalid')
            run('remote', 'add', 'origin', str(remote))
            (work / 'README').write_text('fake repo\n')
            run('add', 'README')
            run('commit', '-m', 'Initial')
            with patch.object(release, 'ROOT', work):
                for args, expected in [(['code'], False), (['with-data', '--data-sha256', 'b' * 64], True), (['code'], False)]:
                    with patch.object(sys, 'argv', ['release.py', *args]):
                        release.main()
                    self.assertEqual('Tacare-Data-SHA256:' in run('log', '-1', '--format=%B'), expected)
                    self.assertEqual(run('rev-parse', 'HEAD'), run('rev-parse', 'origin/main'))
                previous = run('rev-parse', 'HEAD')
                (work / 'README').write_text('uncommitted\n')
                with patch.object(sys, 'argv', ['release.py', 'code']), self.assertRaises(SystemExit):
                    release.main()
                self.assertEqual(run('rev-parse', 'HEAD'), previous)


if __name__ == '__main__':
    unittest.main()
