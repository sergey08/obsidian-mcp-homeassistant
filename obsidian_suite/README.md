# Obsidian MCP Suite

A single Home Assistant app combining **a private Obsidian MCP server**, an **OpenAI Secure MCP Tunnel client**, and **Self-hosted LiveSync CLI**.

## What it does

- Read, search, create, append, rename and safely delete Obsidian Markdown notes using seven MCP tools.
- Connect ChatGPT to your private Home Assistant installation without opening the MCP server to the internet.
- Synchronize the local vault with your existing LiveSync/CouchDB setup.
- Keep the vault, private trash and credentials in persistent Home Assistant app configuration.
- Start the MCP server before starting the tunnel.

**Important:** the current release supports migrations from an existing `obsidian_bridge` setup and requires manual private provisioning. It is not yet a zero-configuration installation for a new vault.

See [Documentation](DOCS.md), [Changelog](CHANGELOG.md), and [OpenAI tunnel setup](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).
