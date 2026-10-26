"""Tests for private JSON onboarding without touching CouchDB."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("settings_import", ROOT / "settings_import.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class JSONImportTests(unittest.TestCase):
    def test_safe_first_import(self):
        with tempfile.TemporaryDirectory() as d:
            result = mod.import_settings_json(b'{"remoteType":"CouchDB"}', d)
            target = Path(d) / "settings/livesync-operativo.json"
            self.assertTrue(target.is_file())
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertIn("stored securely", result)

    def test_no_overwrite_or_echo(self):
        with tempfile.TemporaryDirectory() as d:
            secret = "super-sensitive-do-not-output"
            mod.import_settings_json(('{"password":"'+secret+'"}').encode(), d)
            with self.assertRaises(mod.SettingsImportError) as cm:
                mod.import_settings_json(('{"password":"'+secret+'"}').encode(), d)
            self.assertNotIn(secret, str(cm.exception))
            self.assertIn(secret, (Path(d)/"settings/livesync-operativo.json").read_text())

    def test_invalid_content(self):
        with tempfile.TemporaryDirectory() as d:
            for value in (b"", b"{}", b"[]", b"not JSON", b"x" * 131073):
                with self.subTest(value=value[:8]):
                    with self.assertRaises(mod.SettingsImportError):
                        mod.import_settings_json(value, d)

    def test_form_does_not_accept_setup_uri(self):
        text = (ROOT / "onboarding.py").read_text(encoding="utf-8")
        self.assertIn('CSRF_TOKEN', text)
        self.assertIn('parse_qs', text)
        self.assertIn('import_settings_json', text)
        self.assertNotIn('import_setup_uri(', text)

if __name__ == "__main__":
    unittest.main()
