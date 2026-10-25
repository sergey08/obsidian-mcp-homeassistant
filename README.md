![Obsidian MCP Suite](docs/logo.png)

# Obsidian MCP for Home Assistant

A Home Assistant app repository for connecting a locally synchronized **Obsidian Markdown vault** to ChatGPT through the **Model Context Protocol (MCP)** and **OpenAI Secure MCP Tunnel**.

## Recommended: Unified Obsidian MCP Suite

The [Obsidian MCP Suite](obsidian_suite/README.md) combines three services into **one Home Assistant app**:

- **MCP server**: seven tools to list, search, read, create, append, rename and safely delete Markdown notes.
- **Secure MCP Tunnel**: private access from ChatGPT without exposing the MCP port to the internet.
- **LiveSync CLI**: replication with an existing Self-hosted LiveSync / CouchDB setup.

**Current release: 0.2.0**. Tested as a migration of an existing `obsidian_bridge` setup on amd64 Home Assistant OS. Fresh installs still require manually provisioning the local vault and private OpenAI tunnel client credentials.

### Installation

1. Add this repository under **Home Assistant > Settings > Apps > App Store > Repositories**:
   `https://github.com/sergey08/obsidian-mcp-homeassistant`
2. Install **Obsidian MCP Suite**.
3. Follow the [full setup, configuration and tunnel guide](obsidian_suite/DOCS.md).
4. Keep duplicate tunnel and LiveSync services stopped during migration.

### Where to obtain an OpenAI tunnel

Create or manage your tunnel at [OpenAI Platform Tunnels](https://platform.openai.com/settings/organization/tunnels). The tunnel ID (`tunnel_...`) is **not** your runtime API key. The executable and key must be provisioned privately. Read the [step-by-step tunnel instructions](obsidian_suite/DOCS.md#getting-an-openai-tunnel).

## Repository folders

- [`obsidian_suite/`](obsidian_suite/) — **recommended unified Home Assistant app**
- [`obsidian_mcp/`](obsidian_mcp/) — legacy standalone MCP
- [`obsidian_tunnel/`](obsidian_tunnel/) — legacy standalone tunnel
- [`obsidian_livesync/`](obsidian_livesync/) — legacy standalone LiveSync

The separate apps are retained as migration/rollback options.

## Security

Never commit vault data, CouchDB passwords, tunnel API keys, or other secrets. The MCP server is not independently authenticated; do not publish its HTTP port. Authorize ChatGPT access only through a properly scoped OpenAI Secure MCP Tunnel.
