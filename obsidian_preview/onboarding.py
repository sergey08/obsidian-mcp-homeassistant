#!/usr/bin/env python3
"""Read-only, local onboarding status page for Home Assistant Ingress.

No secrets or note contents are returned. Supervisor Ingress provides access
control; this server must never be published as a host port.
"""
import html
import json
import os
import secrets
from urllib.parse import parse_qs, urlsplit
from settings_import import import_settings_json, SettingsImportError
from couchdb_check import check_couchdb, check_couchdb_values, CouchCheckError
from tunnel_key import store_runtime_key, TunnelKeyError
from livesync_setup import save_profile, SetupError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DATA = Path("/data")
LEGACY = Path("/app_configs/obsidian_bridge")
CSRF_TOKEN = secrets.token_urlsafe(32)
MAX_REQUEST = 180000
I18N = {
 "en": {
  "heading":"Obsidian MCP for Home Assistant", "subtitle":"Initial setup — Preview",
  "warning":"File presence alone does not confirm connectivity or the authenticity of the tunnel client.",
  "requirement":"Requirement","status":"Status","next":"Next step","ready":"Ready","missing":"Not configured",
  "vault":"Local Markdown vault","trash":"Recoverable trash","sync_settings":"LiveSync settings",
  "sync_enabled":"LiveSync enabled","tunnel_binary":"Tunnel client executable",
  "tunnel_key":"Tunnel runtime key","tunnel_id":"Tunnel ID","tunnel_enabled":"Tunnel enabled",
  "vault_hint":"Created automatically","trash_hint":"Created automatically",
  "sync_settings_hint":"Import settings from your Obsidian client",
  "sync_enabled_hint":"Enable after verifying synchronization",
  "tunnel_binary_hint":"Check the official executable and its provenance before enabling",
  "tunnel_key_hint":"Store your private runtime key; validity is not verified here",
  "tunnel_id_hint":"Enter the ID in the add-on Configuration tab",
  "tunnel_enabled_hint":"Enable only after completing setup",
  "guided_title":"Configure CouchDB manually","guided_url":"Server URL","guided_db":"Database name","guided_user":"Username","guided_password":"Password","guided_passphrase":"Shared encryption passphrase (optional for unencrypted setup)","guided_encrypted":"Enable encryption","guided_button":"Save CouchDB configuration","guided_test":"Test connection without saving","sync_title":"1. LiveSync configuration","sync_desc":"Paste trusted LiveSync CLI settings JSON, not an obsidian:// setup URI. Test only with a disposable database.",
  "sync_label":"LiveSync settings JSON","sync_button":"Import settings once",
  "check_title":"Check CouchDB connectivity","check_desc":"Read-only connectivity and authentication check. Does not start replication.",
  "check_button":"Check CouchDB","key_title":"2. ChatGPT tunnel key",
  "key_desc":"Use only your own organization's tunnel runtime key. It is stored locally and never shown again.",
  "key_label":"Runtime API key","key_button":"Store private key",
  "docs":"Setup documentation","disclaimer":"Do not enter production credentials in this preview installation.",
  "unknown":"Request completed"
 },
 "es": {
  "heading":"Obsidian MCP para Home Assistant","subtitle":"Configuración inicial — Versión de pruebas",
  "warning":"La presencia de archivos no confirma la conexión ni la autenticidad del cliente del túnel.",
  "requirement":"Requisito","status":"Estado","next":"Siguiente paso","ready":"Preparado","missing":"Sin configurar",
  "vault":"Bóveda Markdown local","trash":"Papelera recuperable","sync_settings":"Configuración de LiveSync",
  "sync_enabled":"LiveSync activado","tunnel_binary":"Ejecutable del túnel",
  "tunnel_key":"Clave privada del túnel","tunnel_id":"Identificador del túnel","tunnel_enabled":"Túnel activado",
  "vault_hint":"Creada automáticamente","trash_hint":"Creada automáticamente",
  "sync_settings_hint":"Importa la configuración desde tu cliente Obsidian",
  "sync_enabled_hint":"Actívalo después de verificar la sincronización",
  "tunnel_binary_hint":"Instala el ejecutable oficial y verifica su procedencia",
  "tunnel_key_hint":"Guarda tu clave privada; aquí no se comprueba su validez",
  "tunnel_id_hint":"Introduce el identificador en la pestaña Configuración",
  "tunnel_enabled_hint":"Actívalo solo después de completar la configuración",
  "guided_title":"Configurar CouchDB manualmente","guided_url":"URL del servidor","guided_db":"Nombre de base de datos","guided_user":"Usuario","guided_password":"Contraseña","guided_passphrase":"Frase de cifrado compartida (opcional sin cifrado)","guided_encrypted":"Activar cifrado","guided_button":"Guardar configuración de CouchDB","guided_test":"Probar conexión sin guardar","sync_title":"1. Configuración de LiveSync","sync_desc":"Pega el JSON de LiveSync CLI de una fuente fiable, nunca un enlace obsidian://. Prueba solo con una base de datos desechable.",
  "sync_label":"JSON de configuración de LiveSync","sync_button":"Importar una sola vez",
  "check_title":"Comprobar conexión CouchDB","check_desc":"Comprueba conexión y autenticación en modo de solo lectura. No inicia sincronización.",
  "check_button":"Comprobar CouchDB","key_title":"2. Clave del túnel de ChatGPT",
  "key_desc":"Utiliza exclusivamente una clave privada de tu propia organización. Se guarda localmente y no vuelve a mostrarse.",
  "key_label":"Clave de ejecución","key_button":"Guardar clave privada",
  "docs":"Documentación de instalación","disclaimer":"No introduzcas credenciales de producción en esta versión de pruebas.",
  "unknown":"Solicitud completada"
 }
}


def collect_status(data=DATA, legacy=LEGACY):
    base = legacy if (legacy / "vault").is_dir() else data
    try:
        options = json.loads((data / "options.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        options = {}
    def exists(path):
        return path.is_file() and path.stat().st_size > 0
    tunnel = bool(options.get("enable_tunnel", False))
    sync = bool(options.get("enable_livesync", False))
    return {
        "vault": (base / "vault").is_dir(),
        "trash": (base / "mcp-trash").is_dir(),
        "sync_enabled": sync,
        "sync_settings": exists(base / "settings/livesync-operativo.json"),
        "tunnel_enabled": tunnel,
        "tunnel_id": bool(str(options.get("tunnel_id", "")).strip()),
        "tunnel_binary": (base / "tunnel/bin/tunnel-client").is_file() and os.access(base / "tunnel/bin/tunnel-client", os.X_OK),
        "tunnel_key": exists(base / "tunnel/api-key"),
    }

def render_page(status, message="", lang="en"):
    lang = lang if lang in I18N else "en"
    tr = I18N[lang]
    rows = []
    for key in ("vault","trash","sync_settings","sync_enabled","tunnel_binary","tunnel_key","tunnel_id","tunnel_enabled"):
        hint = tr.get(key + "_hint", "")
        rows.append("<tr><td>"+html.escape(tr[key])+"</td><td><span class='state'>"+
                    ("✓ "+tr["ready"] if status[key] else "— "+tr["missing"])+
                    "</span></td><td>"+html.escape(hint)+"</td></tr>")
    form = ""
    hidden = "<input type='hidden' name='csrf' value='" + CSRF_TOKEN + "'>"
    hidden += "<input type='hidden' name='lang' value='" + lang + "'>"
    if not status["sync_settings"] and not status["sync_enabled"]:
        form += ("<section><h2>"+tr["sync_title"]+"</h2><p>"+tr["sync_desc"]+"</p>"
                 "<form method='post' action='./'>"+hidden+
                 "<label for='settings'>"+tr["sync_label"]+"</label>"
                 "<textarea name='settings' id='settings' rows='6' required autocomplete='off' spellcheck='false'></textarea>"
                 "<button type='submit'>"+tr["sync_button"]+"</button></form></section>")
    if not status["sync_settings"] and not status["sync_enabled"]:
        fields = (("couch_url","guided_url","url"),("couch_db","guided_db","text"),
                  ("couch_user","guided_user","text"),("couch_password","guided_password","password"),
                  ("couch_passphrase","guided_passphrase","password"))
        controls = ""
        for key,label,kind in fields:
            controls += ("<label for='"+key+"'>"+tr[label]+"</label>"
                         "<input id='"+key+"' name='"+key+"' type='"+kind+"' "+
                         ("required " if key != "couch_passphrase" else "")+
                         "autocomplete='off' maxlength='4096'>")
        form += ("<section><h2>"+tr["guided_title"]+"</h2>"
                 "<form method='post' action='./'>"+hidden+
                 "<input type='hidden' name='action' value='save_couch_profile'>"
                 +controls+"<label><input type='checkbox' name='couch_encrypted' value='1' checked "
                 "style='width:auto'> "+tr["guided_encrypted"]+"</label>"
                 "<button type='submit'>"+tr["guided_button"]+"</button>"
                 "<button type='submit' name='action' value='test_couch_profile' style='margin-left:10px;background:#34354a;color:white'>"+tr["guided_test"]+"</button></form></section>")
    if status["sync_settings"]:
        form += ("<section><h2>"+tr["check_title"]+"</h2><p>"+tr["check_desc"]+"</p>"
                 "<form method='post' action='./'>"+hidden+
                 "<input type='hidden' name='action' value='check_couchdb'>"
                 "<button type='submit'>"+tr["check_button"]+"</button></form></section>")
    if not status["tunnel_key"] and not status["tunnel_enabled"]:
        form += ("<section><h2>"+tr["key_title"]+"</h2><p>"+tr["key_desc"]+"</p>"
                 "<form method='post' action='./'>"+hidden+
                 "<input type='hidden' name='action' value='save_tunnel_key'>"
                 "<label for='tunnel_key'>"+tr["key_label"]+"</label>"
                 "<input name='tunnel_key' id='tunnel_key' type='password' required autocomplete='new-password'>"
                 "<button type='submit'>"+tr["key_button"]+"</button></form></section>")
    notice = "<p role='status' class='notice'>"+html.escape(message)+"</p>" if message else ""
    css = ("body{font:15px system-ui,sans-serif;background:#151723;color:#f4f5fb;margin:0;line-height:1.5}"
           "main{max-width:960px;margin:auto;padding:28px 20px}h1{font-size:1.8rem;margin:0;color:#c5aaff}"
           "h2{font-size:1.15rem;margin:0 0 12px}p{color:#c5c8d7}"
           ".top{display:flex;justify-content:space-between;align-items:start;gap:16px;flex-wrap:wrap}"
           ".lang a{display:inline-block;padding:7px 12px;border:1px solid #56566c;border-radius:8px;"
           "color:#eee;text-decoration:none;margin-left:4px}.lang a[aria-current=page]{background:#564481}"
           ".scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;min-width:520px}"
           "th,td{text-align:left;padding:12px;border-bottom:1px solid #444758}th{color:#c5aaff}"
           "section{background:#202331;border:1px solid #383b50;border-radius:12px;padding:22px;margin:22px 0}"
           "label{display:block;margin:15px 0 6px;font-weight:600}"
           "textarea,input{box-sizing:border-box;width:100%;padding:11px;background:#131623;color:white;"
           "border:1px solid #696d80;border-radius:7px}"
           "button{background:#a888ef;color:#14121d;border:0;border-radius:8px;padding:11px 19px;"
           "font-weight:700;margin-top:14px;cursor:pointer}"
           ".notice{border-left:3px solid #ad91f0;padding:10px;background:#252238}"
           ".state{white-space:nowrap}.muted{font-size:13px}")
    return ("<!doctype html><html lang='"+lang+"'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Obsidian MCP Preview</title><style>"+css+"</style><main>"
            "<div class='top'><div><h1>"+tr["heading"]+"</h1><p>"+tr["subtitle"]+"</p></div>"
            "<nav class='lang' aria-label='Language / Idioma'>"
            "<a href='?lang=es' "+("aria-current='page'" if lang=="es" else "")+">Español</a>"
            "<a href='?lang=en' "+("aria-current='page'" if lang=="en" else "")+">English</a></nav></div>"
            "<p>"+tr["warning"]+"</p><div class='scroll'><table><thead><tr>"
            "<th>"+tr["requirement"]+"</th><th>"+tr["status"]+"</th><th>"+tr["next"]+"</th>"
            "</tr></thead><tbody>"+"".join(rows)+"</tbody></table></div>"
            +notice+form+"<p class='muted'>"+tr["disclaimer"]+"</p>"
            "<p><a style='color:#bfa5ff' href='https://github.com/sergey08/obsidian-mcp-homeassistant/blob/feature/fresh-install-onboarding/obsidian_preview/TESTING.md'"
            " target='_blank' rel='noopener noreferrer'>"+tr["docs"]+"</a></p></main></html>")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] not in ("/", "/index.html"):
            self.send_error(404)
            return
        params = parse_qs(urlsplit(self.path).query)
        lang = params.get("lang", ["en"])[0]
        content = render_page(collect_status(), lang=lang).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'self'")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
    def do_POST(self):
        # CSRF-protected Ingress-only action; no request contents in logs/errors.
        length = self.headers.get("Content-Length", "")
        if not length.isdecimal() or not 0 < int(length) <= MAX_REQUEST:
            self.send_error(413)
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/x-www-form-urlencoded":
            self.send_error(415)
            return
        try:
            data = parse_qs(self.rfile.read(int(length)).decode("utf-8"), strict_parsing=True)
        except (ValueError, UnicodeDecodeError):
            self.send_error(400)
            return
        if data.get("csrf") != [CSRF_TOKEN]:
            self.send_error(403)
            return
        status = collect_status()
        if data.get("action") == ["save_tunnel_key"]:
            base = LEGACY if (LEGACY / "vault").is_dir() else DATA
            if status["tunnel_enabled"] or status["tunnel_key"]:
                message = "Import refused: tunnel is enabled or key already exists."
            else:
                try:
                    message = store_runtime_key(data.get("tunnel_key", [""])[0], base)
                except TunnelKeyError as exc:
                    message = str(exc)
        elif data.get("action") == ["test_couch_profile"]:
            cfg = {"couchDB_URI": data.get("couch_url", [""])[0],
                   "couchDB_DBNAME": data.get("couch_db", [""])[0],
                   "couchDB_USER": data.get("couch_user", [""])[0],
                   "couchDB_PASSWORD": data.get("couch_password", [""])[0]}
            try:
                message = check_couchdb_values(cfg)
            except CouchCheckError as exc:
                message = str(exc)
        elif data.get("action") == ["save_couch_profile"]:
            base = LEGACY if (LEGACY / "vault").is_dir() else DATA
            if status["sync_enabled"] or status["sync_settings"]:
                message = "Import refused: LiveSync is enabled or settings already exist."
            else:
                try:
                    message = save_profile(
                        data.get("couch_url", [""])[0], data.get("couch_db", [""])[0],
                        data.get("couch_user", [""])[0], data.get("couch_password", [""])[0],
                        data.get("couch_passphrase", [""])[0],
                        data.get("couch_encrypted", []) == ["1"], base)
                except SetupError as exc:
                    message = str(exc)
        elif data.get("action") == ["check_couchdb"]:
            base = LEGACY if (LEGACY / "vault").is_dir() else DATA
            try:
                message = check_couchdb(base / "settings/livesync-operativo.json")
            except CouchCheckError as exc:
                message = str(exc)
        elif status["sync_enabled"] or status["sync_settings"]:
            message = "Import refused: LiveSync is enabled or settings already exist."
        else:
            base = LEGACY if (LEGACY / "vault").is_dir() else DATA
            try:
                message = import_settings_json(data.get("settings", [""])[0].encode("utf-8"), base)
            except SettingsImportError as exc:
                message = str(exc)
        lang = data.get("lang", ["en"])[0]
        content = render_page(collect_status(), message, lang=lang).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8099), Handler).serve_forever()
