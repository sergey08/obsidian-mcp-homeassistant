# Obsidian Tunnel (Preview)

This add-on wraps a **locally supplied** tunnel client binary. It does **not** download or redistribute OpenAI's tunnel client.

## Security and deployment limitations

- **Do not start while an existing tunnel with the same tunnel ID is active.** Two concurrent authenticated clients can disrupt connectivity.
- Do not publish tunnel credentials, vaults, host `docker inspect` output, or the client binary in GitHub.
- The add-on expects files in its shared app-config mapping:
  - `/app_configs/obsidian_bridge/tunnel/bin/tunnel-client`
  - `/app_configs/obsidian_bridge/tunnel/api-key`
- The add-on's startup script reads `tunnel_id` and `mcp_server_url` from Supervisor options; the tunnel ID is installation-specific.
- Default MCP target is the current lab repository's slug. Change this setting if the installed MCP add-on has another slug.
- Test the target MCP first and preserve rollback instructions before cutover.
- This preview is **not** a general-purpose publicly installable tunnel package: it requires a user-provisioned compatible client and a valid tunnel registration.
- Alpine has no built-in mechanism to update the client binary; keep it maintained separately.
- The preview is intended to be installed but left **stopped** until a planned cutover.
