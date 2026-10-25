# 🧪 Obsidian MCP Preview — isolated Home Assistant test

**English / Español**

## English — manual installation
1. Open [GitHub Actions preview build](https://github.com/sergey08/obsidian-mcp-homeassistant/actions/workflows/preview-addon-build.yml), select the latest successful run on `feature/fresh-install-onboarding`, and download artifact `obsidian-preview-0.3.0-dev1`.
2. Extract the GitHub artifact ZIP, then extract any inner ZIP. Locate the `obsidian_preview` directory containing `config.yaml` and `Dockerfile`.
3. Using Samba or a supported File Browser on Home Assistant, put that **directory itself** under Home Assistant's local add-ons directory (`addons/local/obsidian_preview/` when viewed via Samba's `addons` share). Do not place it in `/config/custom_components`.
4. In Home Assistant: **Settings → Apps → App Store → ⋮ → Check for updates / Reload**. Open **Obsidian MCP PREVIEW (experimental)**, install it, leave LiveSync and tunnel **disabled**, and start.
5. Confirm **Open Web UI** displays the onboarding checklist and that an empty vault is created. Never import production LiveSync settings or your production tunnel key during initial tests.
6. Test with a disposable CouchDB database and test notes only. Keep the stable Obsidian MCP app unchanged. Both apps may have their own MCP port inside distinct app containers.
7. Stop/remove the preview app after testing; delete only preview-owned data, never the stable app's or the separate Obsidian Sync Server's data.

**Current scope:** Builds and Docker first-boot tests passed. Actual Supervisor installation and Ingress session behavior are **unverified**. This package is not a stable release.

## Español — instalación manual
1. Abre las [compilaciones de GitHub Actions](https://github.com/sergey08/obsidian-mcp-homeassistant/actions/workflows/preview-addon-build.yml), selecciona la última ejecución correcta de `feature/fresh-install-onboarding` y descarga `obsidian-preview-0.3.0-dev1`.
2. Descomprime el archivo descargado y, si contiene otro ZIP, descomprímelo también. Debe quedar una carpeta `obsidian_preview` que contenga `config.yaml` y `Dockerfile`.
3. Copia esa carpeta a los complementos locales mediante Samba o File Browser; la ruta habitual en el recurso Samba `addons` es `addons/local/obsidian_preview/`. No la copies en `custom_components`.
4. En Home Assistant ve a **Ajustes → Aplicaciones → Tienda → ⋮ → Buscar actualizaciones/Recargar**. Instala **Obsidian MCP PREVIEW (experimental)**, deja LiveSync y el túnel **desactivados** y arranca la aplicación.
5. Abre **Open Web UI** y verifica la lista de preparación. No importes credenciales, bóvedas ni configuraciones de producción.
6. Para probar LiveSync utiliza una base CouchDB desechable y notas temporales. No cambies ni pares el complemento estable.
7. Al terminar, detén o elimina únicamente la versión Preview; no borres datos del complemento estable ni del servidor Obsidian Sync Server.

**Pendiente:** validar Supervisor e Ingress reales. El paquete experimental **no es una versión estable**.
