![Obsidian MCP for Home Assistant](docs/logo.png)

# Obsidian MCP for Home Assistant

A Home Assistant OS add-on repository hosting a seven-tool [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for a locally synchronized Obsidian Markdown vault.

> **Preview, version 1.0.0.** This add-on has not yet been built and tested on the target Home Assistant installation. Keep the existing MCP server, LiveSync bridge, and tunnel running during evaluation.

## Features

- List, search, and read Markdown notes.
- Create, append, rename, and move notes to recoverable trash.
- Save a previous version before overwriting an existing note.
- MCP Streamable HTTP transport via Python FastMCP.
- Reuse the existing vault and trash folders without moving the notes.

## Install via Home Assistant

1. In Home Assistant, open **Settings > Apps > App Store** and the repository menu.
2. Add this repository URL: `https://github.com/sergey08/obsidian-mcp-homeassistant`.
3. Install **Obsidian MCP (Preview)**, but do not stop the original Docker services.
4. Inspect add-on logs and verify mounts before performing any note writes.
5. Leave the MCP HTTP port unpublished until a secure connection and cutover plan are ready.

This repository is currently **private**. Git-based installation may require authentication or a public repository; the Supervisor cannot be assumed to access a private repository merely because ChatGPT is authorized.

## Data layout

The add-on expects the Supervisor app-config mount:
- `/app_configs/obsidian_bridge/vault`
- `/app_configs/obsidian_bridge/mcp-trash`

The original host paths live under `/mnt/data/supervisor/app_configs/obsidian_bridge/`. Do not add this directory, credentials, or private vault content to the Git repository.

## Operational limitations

- The add-on replaces **only** the Python MCP service. LiveSync CLI and the ChatGPT tunnel require separate migration work.
- The Python service currently has no built-in authentication. Do **not** publish the port to an untrusted network.
- The original tunnel points to `127.0.0.1:8765/mcp`; installing the new add-on does not automatically switch it.
- The build, app-config permissions and lifecycle still require validation.
- No current production containers are modified by publishing this repository.

## Source layout

```text
repository.yaml
obsidian_mcp/
  config.yaml
  Dockerfile
  run.sh
  server.py
  DOCS.md
```
