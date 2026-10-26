"""Offline checks for the full-snapshot archive boundary; no Docker or server."""
import importlib.util
import io
from pathlib import Path
import tarfile
import unittest

spec=importlib.util.spec_from_file_location('snapshot',Path(__file__).parents[1]/'prepare_full_snapshot.py')
snapshot=importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class ArchiveBoundary(unittest.TestCase):
    def archive(self, names, kind=tarfile.REGTYPE):
        data=io.BytesIO()
        with tarfile.open(fileobj=data,mode='w') as output:
            for name in names:
                entry=tarfile.TarInfo(name);entry.type=kind
                if kind==tarfile.SYMTYPE:entry.linkname='/tmp/outside'
                output.addfile(entry)
        data.seek(0)
        return tarfile.open(fileobj=data,mode='r')

    def test_accepts_only_regular_filestore_members(self):
        with self.archive(['tacare_local/ab/abc','tacare_local/checklist/ab/abc']) as archive:
            self.assertEqual(len(snapshot.checked_members(archive)),2)

    def test_rejects_other_database_absolute_or_parent_paths(self):
        for name in ['another_db/ab/abc','/tacare_local/ab/abc','tacare_local/../outside']:
            with self.subTest(name=name), self.archive([name]) as archive:
                with self.assertRaises(ValueError):snapshot.checked_members(archive)

    def test_rejects_links_devices_and_duplicate_paths(self):
        for kind in [tarfile.SYMTYPE,tarfile.LNKTYPE,tarfile.FIFOTYPE,tarfile.CHRTYPE]:
            with self.subTest(kind=kind),self.archive(['tacare_local/ab/abc'],kind) as archive:
                with self.assertRaises(ValueError):snapshot.checked_members(archive)
        with self.archive(['tacare_local/ab/abc','tacare_local/ab/abc']) as archive:
            with self.assertRaises(ValueError):snapshot.checked_members(archive)


if __name__=='__main__':unittest.main()
