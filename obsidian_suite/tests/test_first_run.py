"""Offline regression checks for the fresh-install storage policy."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class FirstRunChecks(unittest.TestCase):
    def test_preflight_source_compiles(self):
        root = Path(__file__).resolve().parents[1]
        for file in ("preflight.py", "supervisor.py", "server.py"):
            compile((root / file).read_text(encoding="utf-8"), str(root / file), "exec")

    def test_fresh_install_defaults_are_disabled(self):
        root = Path(__file__).resolve().parents[1]
        data = (root / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("enable_livesync: false", data)
        self.assertIn("enable_tunnel: false", data)

    def test_livesync_uses_separate_database_directory(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "supervisor.py").read_text(encoding="utf-8")
        self.assertIn('db_path = BASE / "livesync-db"', source)
        self.assertIn('"/usr/local/bin/livesync-cli", "--settings"', source)
        self.assertIn('"LIVESYNC_DB_PATH": str(db_path)', source)

    def test_managed_vault_and_trash_reject_symlinks(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "supervisor.py").read_text(encoding="utf-8")
        self.assertIn("for folder in (vault, trash):", source)
        self.assertIn("if folder.is_symlink():", source)
        self.assertIn("Managed storage path must not be a symbolic link", source)

    def test_no_sensitive_values_in_preflight_output(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "preflight.py").read_text(encoding="utf-8")
        self.assertNotIn("print(options)", source)
        self.assertNotIn("print(key.read_text", source)
        self.assertNotIn("subprocess.", source)


if __name__ == "__main__":
    unittest.main()
