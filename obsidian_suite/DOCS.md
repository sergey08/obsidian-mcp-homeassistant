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


## Tested migration and recovery checklist

1. Verify `Obsidian MCP Suite` is installed and its options contain the original tunnel ID (not a new ID).
2. Stop the original Tunnel, LiveSync and MCP add-ons before starting the suite. Never run two LiveSync writers or two tunnels with the same tunnel ID.
3. Start the suite, review add-on logs for `MCP TCP endpoint is ready`, `mcp session initialized`, and `Initial replication complete`.
4. From ChatGPT, list and read notes, create a temporary Markdown note, and confirm it arrives at another Obsidian client.
5. Delete the temporary note via MCP after the second-client check; a recoverable copy remains in the private trash.
6. Keep old add-ons installed, but stopped, until after verification; then uninstall them only after backing up the vault, settings and tunnel configuration.

### Recovery if the suite stops working

1. Stop `Obsidian MCP Suite` first.
2. Start the original `Obsidian MCP` add-on.
3. Start the original `Obsidian LiveSync Bridge` add-on.
4. Start the original `Obsidian Tunnel` add-on.
5. Confirm the connection from ChatGPT and sync from another Obsidian client.

**Never publish tunnel credentials, CouchDB passwords, the vault contents, or private configuration files.** Changes to the add-on code do not require moving those files.
