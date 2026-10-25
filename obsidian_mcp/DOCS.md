# Obsidian MCP (Preview)

A Streamable HTTP MCP server for Markdown notes, adapted from the existing working deployment.

## Safety and migration

- Preview build. Do not stop or remove the existing `obsidian-mcp`, `obsidian-livesync-bridge`, or `obsidian-tunnel` containers.
- Uses the existing data under `/app_configs/obsidian_bridge` via the Supervisor `all_app_configs` mount.
- The port is **not published** by default. Test locally before cutover.
- The server supports writing and deleting notes. Only expose it through a trusted and authenticated transport.
- Backup the vault and trash before testing any write actions.
- The LiveSync bridge and ChatGPT tunnel are **not** included in this add-on.
- Building and runtime behavior must be validated on your Home Assistant OS installation.
