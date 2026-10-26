"""Create LiveSync CLI settings from Home Assistant app options on a fresh install.

Never overwrite an existing profile: existing installations keep working.
Never log values or use credentials in command arguments.
"""
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

class ConfigurationError(Exception):
    pass

def ensure_settings(options, base):
    path = Path(base) / "settings" / "livesync-operativo.json"
    if path.exists() or path.is_symlink():
        if not path.is_file() or path.stat().st_size == 0:
            raise ConfigurationError("Existing LiveSync settings are invalid")
        return "existing"
    uri = str(options.get("couchdb_url", "")).strip().rstrip("/")
    db = str(options.get("couchdb_database", "obsidian")).strip()
    user = str(options.get("couchdb_username", "")).strip()
    password = options.get("couchdb_password", "")
    encrypted = options.get("livesync_encryption", True)
    phrase = options.get("livesync_passphrase", "")
    if not all((uri, db, user, password)):
        raise ConfigurationError("CouchDB URL, database, username and password are required for first setup")
    parsed = urlsplit(uri)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigurationError("CouchDB URL must be HTTP(S) without credentials or query")
    if not db.replace("_","a").replace("-","a").isalnum() or db.lower()!=db:
        raise ConfigurationError("Invalid CouchDB database name")
    if type(encrypted) is not bool or (encrypted and not phrase):
        raise ConfigurationError("A shared passphrase is required when encryption is enabled")
    profile = {
        "couchDB_URI": uri, "couchDB_DBNAME": db,
        "couchDB_USER": user, "couchDB_PASSWORD": password,
        "isConfigured": True, "remoteType": "CouchDB",
        "encrypt": encrypted, "liveSync": True,
        "syncOnSave": True, "syncOnStart": True,
        "usePluginSync": False,
    }
    if encrypted:
        profile["passphrase"] = phrase
    folder=path.parent
    folder.mkdir(mode=0o700,parents=True,exist_ok=True)
    os.chmod(folder,0o700)
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    try:
        fd=os.open(path,flags,0o600)
    except FileExistsError:
        return "existing"
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as out:
            json.dump(profile,out,ensure_ascii=False)
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return "created"
