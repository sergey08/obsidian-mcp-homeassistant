#!/usr/bin/env python3
"""Read-only, local onboarding status page for Home Assistant Ingress.

No secrets or note contents are returned. Supervisor Ingress provides access
control; this server must never be published as a host port.
"""
import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DATA = Path("/data")
LEGACY = Path("/app_configs/obsidian_bridge")

def collect_status(data=DATA, legacy=LEGACY):
    base = legacy if (legacy / "vault").is_dir() else data
    try:
        options = json.loads((data / "options.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        options = {}
    def exists(path):
        return path.is_file() and path.stat().st_size > 0
    tunnel = bool(options.get("enable_tunnel", False))
    sync = bool(options.get("enable_livesync", False))
    return {
        "vault": (base / "vault").is_dir(),
        "trash": (base / "mcp-trash").is_dir(),
        "sync_enabled": sync,
        "sync_settings": exists(base / "settings/livesync-operativo.json"),
        "tunnel_enabled": tunnel,
        "tunnel_id": bool(str(options.get("tunnel_id", "")).strip()),
        "tunnel_binary": (base / "tunnel/bin/tunnel-client").is_file() and os.access(base / "tunnel/bin/tunnel-client", os.X_OK),
        "tunnel_key": exists(base / "tunnel/api-key"),
    }

def render_page(status):
    items = [
        ("Local Markdown vault", status["vault"], "Created on first startup"),
        ("Recoverable trash", status["trash"], "Created on first startup"),
        ("LiveSync settings", status["sync_settings"], "Import settings from your Obsidian client"),
        ("LiveSync enabled", status["sync_enabled"], "Enable only after configuring synchronization"),
        ("Tunnel client executable", status["tunnel_binary"], "Provision an official tunnel-client binary"),
        ("Tunnel runtime key", status["tunnel_key"], "Provision a private runtime key file"),
        ("Tunnel ID set", status["tunnel_id"], "Copy the tunnel ID into Configuration"),
        ("Tunnel enabled", status["tunnel_enabled"], "Enable after provisioning credentials"),
    ]
    rows = "".join(
        "<tr><td>"+html.escape(label)+"</td><td>"+("Ready" if ready else "Not configured")+
        "</td><td>"+html.escape(hint)+"</td></tr>"
        for label, ready, hint in items
    )
    return ("<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Obsidian MCP setup</title>"
        "<style>body{font:16px system-ui;max-width:960px;margin:2em auto;padding:0 1em;"
        "background:#171925;color:#f7f8fc}a{color:#6dd8ff}table{width:100%;border-collapse:collapse}"
        "td,th{padding:12px;border-bottom:1px solid #444;text-align:left}"
        "h1{color:#bda3ff}.hint{color:#bac0d3}</style>"
        "<h1>Obsidian MCP for Home Assistant</h1>"
        "<p>Read-only first-run checklist. No passwords, API keys or note contents are displayed.</p>"
        "<table><thead><tr><th>Requirement</th><th>Status</th><th>Next step</th></tr></thead>"
        "<tbody>"+rows+"</tbody></table>"
        "<p class='hint'>CouchDB connection and end-to-end synchronization have not been verified by this checklist.</p>"
        "<p><a href='https://github.com/sergey08/obsidian-mcp-homeassistant/blob/main/obsidian_suite/DOCS.md'"
        " target='_blank' rel='noopener noreferrer'>Setup documentation</a></p></html>")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] not in ("/", "/index.html"):
            self.send_error(404)
            return
        content = render_page(collect_status()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
    def do_POST(self):
        self.send_error(405)
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8099), Handler).serve_forever()
