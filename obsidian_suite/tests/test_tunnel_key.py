"""Offline tests for secret-safe one-time tunnel key provisioning."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tunnel_key", ROOT / "tunnel_key.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TunnelKeyTests(unittest.TestCase):
    def test_create_private_key_once(self):
        with tempfile.TemporaryDirectory() as d:
            secret = "ci-private-tunnel-key-only"
            result = mod.store_runtime_key(secret, d)
            target = Path(d) / "tunnel/api-key"
            self.assertEqual(target.read_text(), secret)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertNotIn(secret, result)
            with self.assertRaises(mod.TunnelKeyError) as error:
                mod.store_runtime_key("other-private-value-1", d)
            self.assertNotIn(secret, str(error.exception))
            self.assertEqual(target.read_text(), secret)

    def test_invalid_values(self):
        with tempfile.TemporaryDirectory() as d:
            for secret in ("", "tiny", "sensitive\nlinebreak"):
                with self.subTest(secret=repr(secret)):
                    with self.assertRaises(mod.TunnelKeyError):
                        mod.store_runtime_key(secret, d)
            self.assertFalse((Path(d) / "tunnel/api-key").exists())

if __name__ == "__main__":
    unittest.main()
