"""Create a one-time LiveSync CLI CouchDB configuration with no remote writes.

This is a minimal CLI profile, not an Obsidian plugin setup-URI decoder.
Never enable synchronization automatically; test against a disposable DB first.
"""
import ipaddress
import json
import urllib.parse
from settings_import import import_settings_json, SettingsImportError

class SetupError(Exception):
    pass

def prepare_profile(uri, database, username, password, passphrase="", encrypted=True):
    values=(uri,database,username,password,passphrase)
    if not all(isinstance(x,str) for x in values):
        raise SetupError("Invalid configuration values")
    if any(len(x)>4096 or any(c in x for c in "\x00\r\n") for x in values):
        raise SetupError("Invalid characters or length")
    parsed=urllib.parse.urlsplit(uri)
    if parsed.scheme not in ("http","https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SetupError("Use a plain HTTP(S) CouchDB base URL without embedded credentials")
    if not (database and username and password) or not database.replace("_","a").replace("-","a").isalnum() or database.lower()!=database:
        raise SetupError("Enter a valid lowercase database name and credentials")
    if encrypted and not passphrase:
        raise SetupError("Encrypted LiveSync requires its existing shared passphrase")
    if not encrypted and passphrase:
        raise SetupError("Remove the passphrase when encryption is disabled")
    try:
        ip=ipaddress.ip_address(parsed.hostname)
        if ip.is_link_local or ip.is_multicast or ip.is_unspecified:
            raise SetupError("Invalid CouchDB destination")
    except ValueError:
        pass
    cfg={
        "couchDB_URI":uri.rstrip("/"),"couchDB_DBNAME":database,
        "couchDB_USER":username,"couchDB_PASSWORD":password,
        "remoteType":"CouchDB","isConfigured":True,
        "encrypt":bool(encrypted),"usePluginSync":False,
        "suspendFileWatching":False,"maxMTimeForReflectEvents":0,
    }
    if encrypted:
        cfg["passphrase"]=passphrase
    return json.dumps(cfg,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def save_profile(uri,database,username,password,passphrase,encrypted,base):
    payload=prepare_profile(uri,database,username,password,passphrase,encrypted)
    try:
        return import_settings_json(payload,base)
    except SettingsImportError as exc:
        raise SetupError(str(exc)) from None
