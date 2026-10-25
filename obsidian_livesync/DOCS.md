# Obsidian LiveSync Bridge (Preview)

Runs the upstream `ghcr.io/vrtmrz/livesync-cli` daemon inside a Supervisor-managed Home Assistant add-on.

## Migration precautions

**Never start this add-on while the original `obsidian-livesync-bridge` container remains running.** Running two synchronized writers on the same vault can produce conflicts or file corruption.

The add-on expects the existing persistent data at:
- `/app_configs/obsidian_bridge/settings/livesync-operativo.json`
- `/app_configs/obsidian_bridge/vault`

Do not upload the settings JSON or vault data to GitHub. Preserve backups before switching.

The upstream CLI image is currently referenced via `latest`. Before a stable release, pin an audited version or immutable digest and test the executable startup method.

This preview is tailored to an existing local vault and is not yet a generalized, ready-to-use distribution.
