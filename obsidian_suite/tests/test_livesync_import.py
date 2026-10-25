"""Offline importer tests; fake CLI only, no CouchDB or secrets."""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("importer", ROOT / "livesync_import.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ImportTests(unittest.TestCase):
    def test_bad_uri_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(m.ImportErrorSafe):
                m.import_setup_uri("https://example.com/?password=abc", d)
    def test_existing_settings_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "settings/livesync-operativo.json"
            target.parent.mkdir()
            target.write_text("original")
            with self.assertRaises(m.ImportErrorSafe):
                m.import_setup_uri("obsidian://setuplivesync?settings=ABC", d)
            self.assertEqual(target.read_text(), "original")
    def test_fake_cli_import(self):
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d) / "fake-cli"
            fake.write_text("#!/bin/sh\nif [ \"$2\" != \"--settings\" ]; then exit 1; fi\nprintf '{\"ok\": true}' > \"$3\"\n")
            fake.chmod(0o700)
            # Caller supplies an isolated temporary data folder.
            out = Path(d) / "user-data"
            out.mkdir()
            result = m.import_setup_uri("obsidian://setuplivesync?settings=ABC", out, cli=str(fake))
            target = out / "settings/livesync-operativo.json"
            self.assertIn("imported", result)
            self.assertTrue(target.exists())
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
    def test_failed_cli_leaves_no_settings(self):
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d) / "reject"
            fake.write_text("#!/bin/sh\nprintf 'secret-output' >&2\nexit 1\n")
            fake.chmod(0o700)
            out = Path(d) / "user-data"
            out.mkdir()
            with self.assertRaises(m.ImportErrorSafe) as error:
                m.import_setup_uri("obsidian://setuplivesync?settings=ABC", out, cli=str(fake))
            self.assertNotIn("secret-output", str(error.exception))
            self.assertFalse((out / "settings/livesync-operativo.json").exists())

if __name__ == "__main__":
    unittest.main()
