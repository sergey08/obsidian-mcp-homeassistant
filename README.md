> **Repository moved / Repositorio trasladado (2026-10-26)**
>
> The actively maintained Home Assistant app catalog is now **[sergey08/homeassistant-addons](https://github.com/sergey08/homeassistant-addons)**. Install and update Obsidian MCP there. This repository is retained only for historical reference; avoid adding both repositories to Home Assistant.
>
> El catálogo mantenido de aplicaciones para Home Assistant está ahora en **[sergey08/homeassistant-addons](https://github.com/sergey08/homeassistant-addons)**. Instala y actualiza Obsidian MCP desde allí. Este repositorio se conserva solo como referencia histórica; no añadas ambos repositorios a Home Assistant.

![Obsidian MCP for Home Assistant](docs/logo.png)

# Obsidian MCP for Home Assistant

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fsergey08%2Fobsidian-mcp-homeassistant)

**Connect your self-hosted Obsidian notes to ChatGPT through Home Assistant — without publishing your MCP server on the internet.**

This repository provides **Obsidian MCP for Home Assistant**, one Home Assistant add-on combining a Markdown MCP server, an OpenAI Secure MCP Tunnel client and the Self-hosted LiveSync CLI. It lets an authorized ChatGPT connection work with notes stored in a locally synchronized Obsidian vault.

## What can it do?

- **List notes** in your Obsidian vault, including nested folders.
- **Search note contents** and return matching excerpts.
- **Read notes** so ChatGPT can reference your own documentation.
- **Create new Markdown notes** from conversations.
- **Append or update existing notes**, including a recoverable copy before overwriting.
- **Rename or move notes** between folders.
- **Safely delete notes** to a private recoverable trash location.
- **Synchronize notes** with your existing LiveSync/CouchDB database so changes can reach Obsidian on your computer or phone.
- **Access privately from ChatGPT** through OpenAI Secure MCP Tunnel rather than forwarding the unauthenticated MCP HTTP port.

The add-on starts and supervises **three services in one container**: MCP, Tunnel and LiveSync. LiveSync can be disabled in configuration if a separate sync setup is used.

## Recommended local Obsidian sync server for Home Assistant

For the CouchDB backend, we recommend the third-party **[Obsidian Sync Server SSL by alexbelgium](https://github.com/alexbelgium/hassio-addons/tree/master/obsidian_syncserver_ssl)** add-on. It runs a self-hosted CouchDB server inside Home Assistant and can expose HTTPS on port 6984 using existing certificates. It is a **separate prerequisite**, not bundled with this MCP add-on.

[![Add alexbelgium repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Falexbelgium%2Fhassio-addons)

Install alexbelgium's repository using the button above, then install **Obsidian Sync Server SSL**, configure a strong CouchDB password and your trusted SSL certificate/key, and configure the **Self-hosted LiveSync community plugin** in Obsidian on your computer or phone. On mobile, use a trusted HTTPS endpoint. Follow [alexbelgium's documentation](https://github.com/alexbelgium/hassio-addons/blob/master/obsidian_syncserver_ssl/README.md) for its requirements and configuration.

**Important:** this server stores and replicates Obsidian note data; it does not install the Obsidian desktop/mobile application, create our local MCP vault automatically, or provision the OpenAI tunnel. The bridge still needs the configured local vault and LiveSync CLI settings. Do not run Obsidian Sync/iCloud and Self-hosted LiveSync against the same vault without reviewing the upstream warnings.

## Prerequisites — what must already exist?

**This add-on is not an Obsidian desktop/mobile application and does not install or configure CouchDB for you.** It runs on Home Assistant and accesses Markdown files in a synchronized vault. You will need:

| Requirement | Details |
| --- | --- |
| **Home Assistant OS / Supervised** | An installation supporting Supervisor add-ons; this build currently targets **amd64**. |
| **Obsidian vault** | A Markdown vault already available in Home Assistant under `/app_configs/obsidian_bridge/vault`. The Obsidian desktop/mobile app alone is not enough; Home Assistant must have a local copy. |
| **Self-hosted LiveSync / CouchDB** | A working CouchDB-backed sync service if you want automatic bidirectional synchronization with Obsidian clients. An existing **Obsidian Sync Server** add-on can provide the server, but it must be configured separately. This add-on does **not** install that service. |
| **LiveSync configuration** | Existing valid settings at `/app_configs/obsidian_bridge/settings/livesync-operativo.json`, required when the LiveSync option is enabled. |
| **OpenAI tunnel** | An authorized tunnel ID (`tunnel_...`), separately provisioned `tunnel-client` executable and private runtime API key. Required when the ChatGPT tunnel option is enabled. |
| **ChatGPT access** | A ChatGPT workspace that supports connecting a custom MCP server through an OpenAI Secure MCP Tunnel, with appropriate organization/workspace permissions. |

**Existing Home Assistant installation:** If you already run Obsidian LiveSync or an Obsidian Sync Server add-on in HA, **do not uninstall the sync server or remove its data**. The suite needs the existing LiveSync backend and local vault. Avoid running a second LiveSync CLI writer on the same vault.

**New installations:** Provisioning the vault, LiveSync settings and tunnel client is currently **manual**. Installing this repository alone will not automatically create a working Obsidian database, vault or tunnel. See the detailed guide before starting the app.

## Install

1. Click the **Add repository to Home Assistant** button above, or manually add `https://github.com/sergey08/obsidian-mcp-homeassistant` in **Settings > Apps > App Store > Repositories**.
2. Install **Obsidian MCP for Home Assistant** from the app store.
3. Follow the [full setup and requirements guide](obsidian_suite/DOCS.md). Configure the vault, CouchDB LiveSync and tunnel credentials privately.
4. Review the app's **Configuration**, start the add-on and confirm that the MCP connection and synchronization work.
5. If migrating from three older standalone add-ons, stop the old Tunnel, LiveSync CLI and MCP processes before starting the unified app. Never duplicate the same tunnel ID or sync writer.

## How to obtain a ChatGPT tunnel

The tunnel is obtained through [OpenAI Platform — Tunnels](https://platform.openai.com/settings/organization/tunnels), subject to your workspace/organization access. You will need a **tunnel ID**, a **runtime API key** and the **tunnel-client executable**. These are separate components; the key must **not** be committed to GitHub.

Read [the step-by-step tunnel instructions](obsidian_suite/DOCS.md#getting-an-openai-tunnel).

## Documentation and project status

- [Complete Home Assistant documentation and setup](obsidian_suite/DOCS.md)
- [Add-on overview](obsidian_suite/README.md)
- [Changelog](obsidian_suite/CHANGELOG.md)

**Current release: 0.2.1.** Successfully tested on an existing amd64 Home Assistant OS deployment with an already configured vault, CouchDB LiveSync and OpenAI tunnel. A fully guided fresh installation is not yet available.

### Repository structure

- [`obsidian_suite/`](obsidian_suite/) — **recommended unified add-on**
- [`obsidian_mcp/`](obsidian_mcp/) — former standalone MCP add-on
- [`obsidian_tunnel/`](obsidian_tunnel/) — former standalone tunnel add-on
- [`obsidian_livesync/`](obsidian_livesync/) — former standalone LiveSync bridge

## Security

The local MCP server has no standalone HTTP authentication. **Do not expose its port to the internet.** Keep your Obsidian vault, CouchDB credentials, LiveSync settings and tunnel runtime key outside this public repository. Authorize access only for trusted ChatGPT workspaces and users.
