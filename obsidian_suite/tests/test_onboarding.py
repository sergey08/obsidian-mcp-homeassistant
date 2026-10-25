"""Offline tests for the read-only ingress checklist."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("onboarding", ROOT / "onboarding.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class OnboardingTests(unittest.TestCase):
    def test_empty_fresh_install(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            data, legacy = root / "data", root / "legacy"
            data.mkdir()
            (data / "options.json").write_text(json.dumps({"enable_tunnel": False, "enable_livesync": False}))
            result = module.collect_status(data, legacy)
            self.assertFalse(result["vault"])
            self.assertFalse(result["sync_enabled"])
            self.assertFalse(result["tunnel_enabled"])
            self.assertNotIn("api_key", result)
    def test_credentials_not_rendered(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            data, legacy = root / "data", root / "legacy"
            (data / "tunnel").mkdir(parents=True)
            secret = "DONT_PRINT_THIS_SECRET_439"
            (data / "tunnel/api-key").write_text(secret)
            (data / "options.json").write_text(json.dumps({"tunnel_id": "tunnel_private_123"}))
            out = module.render_page(module.collect_status(data, legacy))
            self.assertNotIn(secret, out)
            self.assertNotIn("tunnel_private_123", out)
            self.assertIn("Tunnel runtime key", out)

if __name__ == "__main__":
    unittest.main()
