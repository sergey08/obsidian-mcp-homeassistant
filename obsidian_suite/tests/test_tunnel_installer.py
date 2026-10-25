"""Offline tests for official tunnel client archive verification."""
import hashlib
import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("tunnel_installer",ROOT/"tunnel_installer.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class InstallerTests(unittest.TestCase):
    def prepare(self,d):
        archive=Path(d)/"tunnel-client-v0.0.18-linux-amd64.zip"
        with zipfile.ZipFile(archive,"w") as z:
            z.writestr("tunnel-client",(b"\x7fELF"+bytes([2,1])+bytes(10)+b"\x02\x00\x3e\x00"+bytes(44)))
        sums=Path(d)/"SHA256SUMS.txt"
        sums.write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+"  "+archive.name+"\n")
        return archive,sums
    def test_checksum_and_one_time_install(self):
        with tempfile.TemporaryDirectory() as d:
            archive,sums=self.prepare(d)
            root=Path(d)/"data";root.mkdir()
            msg=m.install_official_archive(archive,sums,root)
            target=root/"tunnel/bin/tunnel-client"
            self.assertTrue(target.read_bytes().startswith(b"\x7fELF"))
            self.assertEqual(target.stat().st_mode & 0o777,0o700)
            self.assertIn("checksum matched",msg)
            with self.assertRaises(m.TunnelInstallError):
                m.install_official_archive(archive,sums,root)
    def test_reject_non_elf(self):
        with tempfile.TemporaryDirectory() as d:
            archive,sums=self.prepare(d)
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("tunnel-client",b"this is not ELF")
            sums.write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+"  "+archive.name+"\\n")
            with self.assertRaises(m.TunnelInstallError):
                m.install_official_archive(archive,sums,Path(d))

    def test_reject_modified_archive(self):
        with tempfile.TemporaryDirectory() as d:
            archive,sums=self.prepare(d)
            archive.write_bytes(archive.read_bytes()+b"tamper")
            with self.assertRaises(m.TunnelInstallError):
                m.install_official_archive(archive,sums,Path(d))
if __name__=="__main__":unittest.main()
