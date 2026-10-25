# Obsidian MCP Suite (Preview)

One Home Assistant add-on containing:
- Obsidian Markdown MCP server (seven tools, port 8765 within its container)
- Locally provisioned ChatGPT tunnel client
- Upstream Obsidian LiveSync CLI

## Migration safety

**Do not start this suite while the existing three add-ons are running.**
Doing so may duplicate the tunnel identity and cause concurrent writes to the vault.

This preview is installed with **manual startup**. No MCP port is exposed on the host. The tunnel reaches the MCP over loopback *inside this add-on*.

### Existing persistent data

The suite uses the existing app-config directory:
- `/app_configs/obsidian_bridge/vault`
- `/app_configs/obsidian_bridge/mcp-trash`
- `/app_configs/obsidian_bridge/settings/livesync-operativo.json`
- `/app_configs/obsidian_bridge/tunnel/bin/tunnel-client`
- `/app_configs/obsidian_bridge/tunnel/api-key`

The tunnel executable and key must be supplied privately. **Never commit these files or vault contents to GitHub.**

### Rollback

Keep the existing three add-ons installed. If the suite fails:
1. Stop the suite.
2. Start the original MCP, then LiveSync, then Tunnel add-ons.
3. Verify the MCP tools and bidirectional LiveSync.

### Release status

Experimental — packaging has not been validated on the target Home Assistant host.
The upstream LiveSync image is pinned to `1.0.39-cli`; test compatibility with your settings before replacing the running version.
No automatic migration or deletion of the old add-ons is performed.
