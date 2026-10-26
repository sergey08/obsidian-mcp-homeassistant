"""Protect the in-place upgrade contract from stable 0.2.1 to 0.2.2.

These checks do not start Home Assistant or modify a real vault.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UpgradeContractTests(unittest.TestCase):
    def test_addon_identity_is_unchanged(self):
        conf = (ROOT / "config.yaml").read_text(encoding="utf-8")
        self.assertIn('slug: "obsidian_suite"', conf)
        self.assertIn('name: "Obsidian MCP for Home Assistant"', conf)
        self.assertNotIn("obsidian_preview", conf)

    def test_existing_configuration_keys_remain_supported(self):
        conf = (ROOT / "config.yaml").read_text(encoding="utf-8")
        for key in ("tunnel_id", "enable_tunnel", "enable_livesync", "livesync_interval"):
            with self.subTest(key=key):
                self.assertIn("  " + key + ":", conf)

    def test_existing_storage_and_secret_locations_are_preserved(self):
        src = (ROOT / "supervisor.py").read_text(encoding="utf-8")
        self.assertIn('Path("/app_configs/obsidian_bridge")', src)
        self.assertIn('BASE / "vault"', src)
        self.assertIn('BASE / "settings/livesync-operativo.json"', src)
        self.assertIn('BASE / "tunnel/api-key"', src)
        self.assertIn('BASE / "tunnel/bin/tunnel-client"', src)

    def test_preview_is_not_a_required_service(self):
        src = (ROOT / "supervisor.py").read_text(encoding="utf-8")
        self.assertNotIn('obsidian_preview', src)


if __name__ == "__main__":
    unittest.main()
