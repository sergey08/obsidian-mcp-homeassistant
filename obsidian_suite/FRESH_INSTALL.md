# Fresh installation (experimental development branch)

This branch is **not a release**. Do not install it on an active vault without backups and a rollback plan.

## For users of alexbelgium Obsidian Sync Server SSL

1. Install and configure the separate [Obsidian Sync Server SSL](https://github.com/alexbelgium/hassio-addons/tree/master/obsidian_syncserver_ssl) add-on and verify syncing from two Obsidian clients using the Self-hosted LiveSync plugin. Other compatible CouchDB setups can also work.
2. Install this MCP add-on **with tunnel and LiveSync disabled**. It creates its owned `/data/vault` and `/data/mcp-trash` folders on first start, while older installations with the existing `obsidian_bridge/vault` continue using the legacy location.
3. Import a Self-hosted LiveSync setup URI from a trusted Obsidian client using the **upstream CLI setup command** (no synchronization performed by `setup`):
   `livesync-cli /data --settings /data/settings/livesync-operativo.json setup "obsidian://setuplivesync?settings=..."`
   This is a **reference command, not an automated wizard**. Handle the setup URI like a password: it can contain private synchronization details. It can be exposed in shell history or process lists; do not paste it into public Issues, screenshots or chat logs. Confirm compatibility with the installed CLI version before using it.
4. Validate HTTPS certificate trust and configuration; then enable LiveSync. Keep any other LiveSync CLI writer stopped.
5. Configure the OpenAI Secure MCP Tunnel separately (official executable + private runtime key + tunnel ID), then enable the tunnel and test a read-only MCP call.

## Current limitations

- The CLI setup URI import, credentials storage, and validation are **not yet integrated into the Home Assistant Configuration UI**.
- The add-on cannot safely infer an encrypted LiveSync setup from CouchDB URL/password alone; use a setup URI exported by a configured Obsidian client.
- There is currently no remote connectivity or encrypted-data compatibility test in the UI.
- The tunnel client binary is still private, manually provisioned, and not bundled.
- Existing working installations are not changed by commits in this feature branch.
- Do not use destructive CLI commands such as `fetch --force` or `rebuild --force` as part of onboarding.

## Diagnostics

The experimental helper `preflight.py` reports which expected files exist without printing secrets or modifying notes. A successful preflight is **not** evidence that replication works: test against a disposable vault first.

### Next engineering work

A secure first-run wizard must allow setup URI import without leaking secrets via URL parameters, command arguments, logs, or shell history; confirm target database and TLS trust; validate before enabling sync; and preserve existing installation rollback.
