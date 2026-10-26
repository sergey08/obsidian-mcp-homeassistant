"""Safe upload of pre-exported LiveSync CLI settings JSON.

This avoids putting a secret setup URI in the CLI process command line.
"""
import json
import os
from pathlib import Path

MAX_SETTINGS_BYTES = 131072

class SettingsImportError(Exception):
    pass

def import_settings_json(raw, base):
    if not isinstance(raw, (bytes, bytearray)) or not 0 < len(raw) <= MAX_SETTINGS_BYTES:
        raise SettingsImportError("Invalid settings file size")
    try:
        obj = json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        raise SettingsImportError("Invalid JSON settings") from None
    if not isinstance(obj, dict) or not obj:
        raise SettingsImportError("Expected a non-empty settings JSON object")
    # We deliberately do not print, transform or infer encrypted settings.
    base = Path(base)
    folder = base / "settings"
    target = folder / "livesync-operativo.json"
    if target.exists() or target.is_symlink():
        raise SettingsImportError("Settings already exist: import refused to prevent overwrite")
    folder.mkdir(parents=True, exist_ok=True)
    os.chmod(folder, 0o700)
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise SettingsImportError("Settings already exist: import refused") from None
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return "Settings file stored securely. Verify compatibility and CouchDB before enabling LiveSync."

def public_profile(base):
    """Return non-sensitive existing CouchDB fields, never secrets."""
    target = Path(base) / "settings/livesync-operativo.json"
    try:
        obj = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return {}
        return {
            "couch_url": str(obj.get("couchDB_URI", "")),
            "couch_db": str(obj.get("couchDB_DBNAME", "")),
            "couch_user": str(obj.get("couchDB_USER", "")),
            "couch_encrypted": "1" if obj.get("encrypt", False) else "0",
            "has_password": bool(obj.get("couchDB_PASSWORD")),
            "has_passphrase": bool(obj.get("passphrase")),
        }
    except (OSError, ValueError):
        return {}

def update_profile(base, changes):
    """Atomically replace settings while sync is externally confirmed stopped."""
    target = Path(base) / "settings/livesync-operativo.json"
    if not target.is_file() or target.is_symlink():
        raise SettingsImportError("Existing settings not found")
    try:
        prior = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(prior, dict):
            raise ValueError()
    except (OSError, ValueError):
        raise SettingsImportError("Existing settings invalid") from None
    mapping = {"couch_url":"couchDB_URI", "couch_db":"couchDB_DBNAME",
               "couch_user":"couchDB_USER", "couch_password":"couchDB_PASSWORD",
               "couch_passphrase":"passphrase"}
    proposed = dict(prior)
    for key,dest in mapping.items():
        val = changes.get(key, "")
        if val:
            proposed[dest] = val
    proposed["encrypt"] = changes.get("couch_encrypted", "0") == "1"
    from livesync_setup import prepare_profile, SetupError
    try:
        prepare_profile(proposed.get("couchDB_URI",""),proposed.get("couchDB_DBNAME",""),
                        proposed.get("couchDB_USER",""),proposed.get("couchDB_PASSWORD",""),
                        proposed.get("passphrase","") if proposed["encrypt"] else "",
                        proposed["encrypt"])
    except SetupError:
        raise SettingsImportError("Invalid CouchDB settings; no changes saved") from None
    if not proposed["encrypt"]:
        proposed.pop("passphrase", None)
    temp = target.with_name(target.name+".new")
    if temp.exists() or temp.is_symlink():
        raise SettingsImportError("Pending settings file already exists")
    raw = json.dumps(proposed,ensure_ascii=False).encode("utf-8")
    if len(raw)>MAX_SETTINGS_BYTES:
        raise SettingsImportError("Settings too large")
    fd = os.open(temp, os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp,target)
    finally:
        temp.unlink(missing_ok=True)
    return "CouchDB settings updated; synchronization remains disabled."
