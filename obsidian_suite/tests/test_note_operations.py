"""Isolated filesystem regression tests for Obsidian MCP note operations.

No production vault, Home Assistant service or CouchDB credentials are used.
"""
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeMCP:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self):
        return lambda function: function


def load_server():
    mcp_module = types.ModuleType("mcp")
    server_module = types.ModuleType("mcp.server")
    fastmcp_module = types.ModuleType("mcp.server.fastmcp")
    fastmcp_module.FastMCP = FakeMCP
    with patch.dict(sys.modules, {
        "mcp": mcp_module, "mcp.server": server_module,
        "mcp.server.fastmcp": fastmcp_module,
    }):
        filename = Path(__file__).resolve().parents[1] / "server.py"
        spec = importlib.util.spec_from_file_location("isolated_obsidian_server", filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class NoteOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.vault = base / "vault"
        self.trash = base / "trash"
        self.vault.mkdir()
        self.trash.mkdir()
        self.server = load_server()
        self.server.ROOT = self.vault.resolve()
        self.server.TRASH = self.trash.resolve()

    def test_create_read_search_and_list(self):
        self.server.write_note("Folder/example.md", "First line\nUnique phrase")
        self.assertEqual(self.server.read_note("Folder/example.md"), "First line\nUnique phrase")
        self.assertEqual(self.server.list_notes(), ["Folder/example.md"])
        self.assertEqual(self.server.search_notes("unique phrase")[0]["line"], 2)

    def test_refuse_overwrite_without_explicit_flag(self):
        self.server.write_note("note.md", "original")
        with self.assertRaises(FileExistsError):
            self.server.write_note("note.md", "replacement")
        self.assertEqual(self.server.read_note("note.md"), "original")

    def test_overwrite_keeps_recoverable_version(self):
        self.server.write_note("note.md", "original")
        self.server.write_note("note.md", "replacement", overwrite=True)
        self.assertEqual(self.server.read_note("note.md"), "replacement")
        backups = list((self.trash / "versions").rglob("note.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "original")

    def test_append_and_rename(self):
        self.server.write_note("old.md", "A")
        self.server.append_note("old.md", "B")
        self.server.rename_note("old.md", "Nested/new.md")
        self.assertEqual(self.server.read_note("Nested/new.md"), "AB")
        self.assertFalse((self.vault / "old.md").exists())

    def test_delete_moves_to_recoverable_trash(self):
        self.server.write_note("to-delete.md", "retain me")
        self.server.delete_note("to-delete.md")
        self.assertFalse((self.vault / "to-delete.md").exists())
        deleted = list((self.trash / "deleted").rglob("to-delete.md"))
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0].read_text(), "retain me")

    def test_reject_traversal_and_symlinks(self):
        for name in ("../outside.md", "/tmp/outside.md", ".hidden.md", "bad.txt"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.server.write_note(name, "unsafe")
        outside = Path(self.tmp.name) / "outside.md"
        outside.write_text("secret")
        (self.vault / "link.md").symlink_to(outside)
        with self.assertRaises(ValueError):
            self.server.read_note("link.md")

    def test_rename_refuses_existing_destination(self):
        self.server.write_note("a.md", "A")
        self.server.write_note("b.md", "B")
        with self.assertRaises(FileExistsError):
            self.server.rename_note("a.md", "b.md")
        self.assertEqual(self.server.read_note("a.md"), "A")
        self.assertEqual(self.server.read_note("b.md"), "B")


if __name__ == "__main__":
    unittest.main()
