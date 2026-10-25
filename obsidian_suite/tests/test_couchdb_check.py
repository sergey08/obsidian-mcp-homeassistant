"""Offline read-only CouchDB checker tests."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("checker", ROOT / "couchdb_check.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, count): return b'{"db_name":"notes"}'

class CouchTests(unittest.TestCase):
    def settings(self, folder, uri="https://example.test:6984", password="secret-123"):
        file = Path(folder) / "settings.json"
        file.write_text(json.dumps({
            "couchDB_URI": uri, "couchDB_DBNAME": "notes",
            "couchDB_USER": "reader", "couchDB_PASSWORD": password
        }))
        return file

    def test_read_only_and_authorization(self):
        with tempfile.TemporaryDirectory() as d:
            settings = self.settings(d)
            with patch.object(mod.urllib.request, "build_opener") as build_mock:
                build_mock.return_value.open.return_value = FakeResponse()
                message = mod.check_couchdb(settings)
                req = build_mock.return_value.open.call_args.args[0]
                self.assertEqual(req.get_method(), "GET")
                self.assertIn("/notes", req.full_url)
                self.assertEqual(req.headers["Authorization"][:6], "Basic ")
                self.assertNotIn("secret-123", message)

    def test_embedded_url_credentials_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            settings = self.settings(d, "https://bad:secret@example.test:6984")
            with self.assertRaises(mod.CouchCheckError):
                mod.check_couchdb(settings)

    def test_error_does_not_echo_secret(self):
        with tempfile.TemporaryDirectory() as d:
            settings = self.settings(d)
            with patch.object(mod.urllib.request, "build_opener") as build_mock:
                build_mock.return_value.open.side_effect = mod.urllib.error.URLError("secret-123")
                with self.assertRaises(mod.CouchCheckError) as err:
                    mod.check_couchdb(settings)
                self.assertNotIn("secret-123", str(err.exception))

    def test_link_local_refused(self):
        with tempfile.TemporaryDirectory() as d:
            settings = self.settings(d, "http://169.254.169.254")
            with self.assertRaises(mod.CouchCheckError):
                mod.check_couchdb(settings)

if __name__ == "__main__":
    unittest.main()
