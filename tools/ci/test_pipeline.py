"""Offline CI boundary regressions; no Docker, SSH or remote Git mutations."""
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ci_runner', Path(__file__).with_name('run_odoo.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def scripts(name):
    lines = (ROOT / '.github/workflows' / name).read_text().splitlines(True)
    blocks = []
    for index, line in enumerate(lines):
        if line == '        run: |\n':
            block = []
            for following in lines[index + 1:]:
                if following.strip() and not following.startswith('          '):
                    break
                block.append(following[10:] if following.startswith('          ') else following)
            blocks.append(''.join(block))
    return blocks


class PipelineTests(unittest.TestCase):
    def test_production_pr_must_come_from_own_uat_branch(self):
        script = scripts('ci.yml')[0]
        environment = {**os.environ, 'SOURCE_BRANCH': 'uat', 'SOURCE_REPOSITORY': 'example/test',
                       'GITHUB_REPOSITORY': 'example/test'}
        for overrides, accepted in (({}, True), ({'SOURCE_BRANCH': 'feature/untested'}, False),
                                    ({'SOURCE_REPOSITORY': 'untrusted/fork'}, False)):
            result = subprocess.run(['bash', '-c', script], env={**environment, **overrides}, capture_output=True)
            self.assertEqual(result.returncode == 0, accepted)

    def test_ci_database_and_addon_targets_are_fixed(self):
        for database in ('tacare_ci', 'tacare_ci_upgrade'):
            self.assertIn('db_host = /ci-socket', runner.config(database))
        for database in ('tacare_local', 'tacare_prod', 'tacare_uat', 'postgres', 'tacare_ci\nadmin_passwd=x'):
            with self.assertRaises(ValueError):
                runner.config(database)
        with self.assertRaises(ValueError):
            runner.config('tacare_ci', '/mnt/production')

    def test_archive_rejects_links_and_path_traversal(self):
        for name, kind in (('../escape', tarfile.REGTYPE), ('/escape', tarfile.REGTYPE),
                           ('source/link', tarfile.SYMTYPE), ('source/link', tarfile.LNKTYPE)):
            raw = io.BytesIO()
            with tarfile.open(fileobj=raw, mode='w') as archive:
                entry = tarfile.TarInfo(name)
                entry.type = kind
                entry.linkname = '/etc/passwd' if kind != tarfile.REGTYPE else ''
                archive.addfile(entry)
            with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
                runner.extract(raw.getvalue(), Path(directory) / 'source')

    def test_archive_extracts_only_to_temporary_source(self):
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w') as archive:
            entry = tarfile.TarInfo('source/addons/module.py')
            entry.size = 5
            archive.addfile(entry, io.BytesIO(b'pass\n'))
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'source'
            runner.extract(raw.getvalue(), target, strip_prefix=True)
            self.assertEqual((target / 'addons/module.py').read_text(), 'pass\n')
            self.assertEqual(target.stat().st_mode & 0o777, 0o755)

    def test_baseline_rejects_shell_or_revision_expressions(self):
        for value in ('HEAD', 'main', '-h', 'a' * 40 + ';id', '../file'):
            with self.assertRaises(ValueError):
                runner.baseline_sha(value)

    def test_stale_commit_skips_and_api_failure_blocks_deployment(self):
        for workflow in ('deploy-uat.yml', 'deploy-tacare.yml'):
            with tempfile.TemporaryDirectory() as directory:
                temporary = Path(directory)
                helper = temporary / 'gh'
                helper.write_text('#!/usr/bin/env bash\n[[ "${API_FAIL:-}" != yes ]] || exit 7\nprintf "%s\\n" "$LATEST_SHA"\n')
                helper.chmod(0o755)
                output = temporary / 'output'
                environment = {**os.environ, 'PATH': directory + ':' + os.environ['PATH'],
                               'GITHUB_REPOSITORY': 'example/test', 'GITHUB_OUTPUT': str(output),
                               'RELEASE_SHA': 'a' * 40, 'LATEST_SHA': 'a' * 40}
                for overrides, expected in (({}, 'deploy=true'), ({'LATEST_SHA': 'b' * 40}, 'deploy=false')):
                    output.write_text('')
                    result = subprocess.run(['bash', '-c', scripts(workflow)[0]], env={**environment, **overrides}, capture_output=True)
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(output.read_text().strip(), expected)
                output.write_text('')
                result = subprocess.run(['bash', '-c', scripts(workflow)[0]], env={**environment, 'API_FAIL': 'yes'}, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(output.read_text(), '')


if __name__ == '__main__':
    unittest.main()
