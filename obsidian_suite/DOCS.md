# Obsidian MCP Suite — User Guide

## Overview

Obsidian MCP Suite runs three services inside **one Home Assistant app**:

1. **MCP server** — seven Markdown tools: list, search, read, write, append, rename and recoverable delete.
2. **OpenAI Secure MCP Tunnel** — makes the local MCP server accessible to your authorized ChatGPT plugin without publishing port 8765.
3. **LiveSync CLI** — synchronizes Markdown notes with the existing CouchDB/Obsidian LiveSync configuration.

The app is currently built for **amd64 Home Assistant OS** and supports an existing, provisioned `obsidian_bridge` vault. It does not create a new vault, CouchDB database or OpenAI account.

## Getting an OpenAI tunnel

The tunnel ID and the runtime API key are **two different things**.

1. Open [OpenAI Platform — Tunnels](https://platform.openai.com/settings/organization/tunnels) and sign in to the organization associated with your ChatGPT workspace.
2. Ensure your Platform role has **Tunnels Read + Manage** to create or manage a tunnel, and **Tunnels Read + Use** to run one. Ask your organization administrator if those permissions are unavailable.
3. Create an MCP tunnel in Platform, or select an existing one you are authorized to use. Associate the tunnel with the intended ChatGPT workspace and Platform organization as appropriate.
4. Copy its **tunnel ID** (format: `tunnel_...`). Enter **only this ID** in the app's **Tunnel ID** configuration field.
5. Create or obtain a **runtime API key** authorized for the tunnel. Do not confuse it with a tunnel ID or an organization admin API key. Keep it out of GitHub, configuration screenshots and chat logs.
6. Download the appropriate `tunnel-client` executable using the Platform instructions or the [latest official GitHub release](https://github.com/openai/tunnel-client/releases/latest). Review the [official quickstart](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) and verify the downloaded executable matches the host architecture.

For this app's **existing installation layout**, the following files must be privately provisioned under the Home Assistant Supervisor app-config storage, not inside the public repository:

| File inside the app | Purpose |
| --- | --- |
| `/app_configs/obsidian_bridge/tunnel/bin/tunnel-client` | Executable OpenAI tunnel client (must have execute permission) |
| `/app_configs/obsidian_bridge/tunnel/api-key` | Runtime API key, stored as the exact secret content |
| `/app_configs/obsidian_bridge/vault` | Markdown vault directory |
| `/app_configs/obsidian_bridge/mcp-trash` | Recoverable MCP trash directory |
| `/app_configs/obsidian_bridge/settings/livesync-operativo.json` | Existing LiveSync settings |

The app reads the API key from a file: it never needs the key pasted into its UI. The `tunnel-client` executable is **not bundled** in this public repository. Do not publish it together with private configuration.

7. In **Home Assistant > Settings > Apps > Obsidian MCP Suite > Configuration**, enable **ChatGPT tunnel** and fill in **Tunnel ID**. Save.
8. Start the suite and inspect **Logs**. Look for `MCP TCP endpoint is ready` and `mcp session initialized`. Your Home Assistant host needs outbound HTTPS access to OpenAI on port 443; no inbound MCP forwarding is required.
9. In **ChatGPT > Plugins > Add custom MCP server**, choose **Tunnel** as the connection type. Select the tunnel or paste the same `tunnel_id`, review permissions and complete creation. If the tunnel is missing, verify the workspace association and permissions.
10. Make a safe test: list or read an innocuous Markdown note. Only consider setup finished when the call succeeds.

See the [official Secure MCP Tunnel documentation](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) for updated UI, permissions, security and troubleshooting.

## Configuration explained

| Field | Default | Description |
| --- | --- | --- |
| **Tunnel ID** (`tunnel_id`) | Empty | Your OpenAI Platform tunnel identifier. Required when tunnel is enabled; **not the runtime API key**. |
| **Enable tunnel** (`enable_tunnel`) | `true` | Start the private ChatGPT tunnel connection. Requires executable, API key file and tunnel ID. |
| **Enable LiveSync** (`enable_livesync`) | `true` | Run continuous synchronization using the existing CouchDB/LiveSync settings. Do not run a second LiveSync writer. |
| **LiveSync interval** (`livesync_interval`) | `60` | Seconds between polling cycles, allowed 30–3600. |

Settings changes may require restarting the app. For an established installation, enable **Start on boot** only after all services have been tested.

## How to use the Information and Logs tabs

The **Information** tab describes the add-on and its version, includes the logo and links to this project. The **Documentation** tab contains this guide, including tunnel provisioning, configuration and recovery. The **Logs** tab shows the startup of all three services.

Expected log signals:
- `MCP TCP endpoint is ready`
- `mcp session initialized`
- `LiveSync is configured and ready`
- `Initial replication complete`

A missing MCP OAuth discovery endpoint may log a 404 warning even when the tunnel works; verify by actually invoking a tool.

## Migration from three separate add-ons

**Never start the unified suite alongside the legacy LiveSync bridge or a second tunnel sharing the same tunnel ID.** Both can cause duplicate sync/writes or tunnel contention.

1. Back up the Obsidian vault, LiveSync settings and tunnel configuration. Keep private secrets out of the repository.
2. Install the suite while the three legacy apps are still installed.
3. Configure the existing tunnel ID. Verify all files above are present.
4. Stop the old **Tunnel**, **LiveSync** and **MCP** apps, then start the unified suite.
5. Confirm the MCP tools work from ChatGPT and that a temporary Markdown note is visible in a second Obsidian client.
6. Delete the test note through MCP (the suite keeps a recoverable copy).
7. After verifying recovery backups, uninstall the stopped legacy apps. **Do not remove the shared `obsidian_bridge` app-config directory or CouchDB add-on.**

## Recovery and diagnostics

If the suite fails after migration:

1. Stop **Obsidian MCP Suite** first.
2. If the former separate apps are still installed, start **MCP**, then **LiveSync**, then **Tunnel**.
3. Test ChatGPT tool access and sync from another Obsidian client.

Common issues:
- **Missing tunnel-client:** download and provision the executable in the private location shown above; give it execute permission.
- **Missing API key:** store a valid runtime key in `tunnel/api-key` privately.
- **Tunnel does not show up in ChatGPT:** check OpenAI workspace/organization association and Tunnels Read + Use permission.
- **Missing vault or settings:** restore from backup and ensure the five required paths exist.
- **Sync conflicts:** stop all duplicate LiveSync clients and inspect CouchDB/LiveSync logs.

**Security:** do not expose the unauthenticated MCP HTTP endpoint publicly; never publish vault notes, API keys or LiveSync secrets. Only use a tunnel with workspaces and people you trust to access or modify the notes.
