"""Read-only CouchDB connectivity test with strict non-secret diagnostics.

Does not create databases, synchronize notes, or relax TLS validation.
Run only on explicit request; do not log endpoints containing credentials.
"""
import base64
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

class CouchCheckError(Exception):
    pass

def check_couchdb(settings_file, timeout=5):
    try:
        cfg = json.loads(Path(settings_file).read_text(encoding="utf-8"))
        uri = cfg["couchDB_URI"]
        db = cfg["couchDB_DBNAME"]
        user = cfg["couchDB_USER"]
        password = cfg["couchDB_PASSWORD"]
        if not all(isinstance(x, str) and x for x in (uri, db, user, password)):
            raise ValueError()
        url = urllib.parse.urlsplit(uri)
        if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError()
        if "/" in db or db in (".", ".."):
            raise ValueError()
        endpoint = urllib.parse.urlunsplit((url.scheme, url.netloc, url.path.rstrip("/") + "/" + urllib.parse.quote(db, safe=""), "", ""))
    except (OSError, ValueError, KeyError, TypeError):
        raise CouchCheckError("Invalid or incomplete CouchDB settings") from None
    auth = base64.b64encode((user + ":" + password).encode("utf-8")).decode("ascii")
    req = urllib.request.Request(endpoint, method="GET", headers={
        "Authorization": "Basic " + auth,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as resp:
            if resp.status != 200:
                raise CouchCheckError("Unexpected CouchDB response")
            raw = resp.read(16384)
            obj = json.loads(raw)
            if not isinstance(obj, dict) or "db_name" not in obj:
                raise CouchCheckError("Target did not return CouchDB database metadata")
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise CouchCheckError("CouchDB authentication or authorization failed") from None
        if exc.code == 404:
            raise CouchCheckError("CouchDB database was not found") from None
        raise CouchCheckError("CouchDB responded with an error") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise CouchCheckError("Cannot reach CouchDB with trusted TLS; check URL, network and certificate") from None
    except (ValueError, json.JSONDecodeError):
        raise CouchCheckError("Unexpected CouchDB response format") from None
    return "CouchDB database is reachable and credentials can read its metadata. LiveSync encryption and replication are not verified."
