"""Single source of truth for runtime controls written by the Ingress UI."""
import json
import os
from pathlib import Path

DEFAULT = {"enable_livesync": False, "enable_tunnel": False, "tunnel_id": "", "livesync_interval": 60}
def load(base=Path("/data")):
    path = Path(base) / "service-config.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(DEFAULT)
    if not isinstance(data, dict):
        return dict(DEFAULT)
    options = {**DEFAULT, **{k: v for k,v in data.items() if k in DEFAULT}}
    if not isinstance(options["enable_livesync"], bool) or not isinstance(options["enable_tunnel"], bool):
        return dict(DEFAULT)
    if not isinstance(options["tunnel_id"], str) or len(options["tunnel_id"]) > 256:
        return dict(DEFAULT)
    if type(options["livesync_interval"]) is not int or not 30 <= options["livesync_interval"] <= 3600:
        return dict(DEFAULT)
    return options

def save(values, base=Path("/data")):
    base=Path(base)
    values = {**DEFAULT, **values}
    if not isinstance(values["enable_livesync"], bool) or not isinstance(values["enable_tunnel"], bool):
        raise ValueError("Invalid runtime switches")
    if not isinstance(values["tunnel_id"], str) or len(values["tunnel_id"]) > 256:
        raise ValueError("Invalid tunnel ID")
    if type(values["livesync_interval"]) is not int or not 30 <= values["livesync_interval"] <= 3600:
        raise ValueError("Invalid LiveSync interval")
    target=base/"service-config.json"
    tmp=base/("."+target.name+"."+str(os.getpid())+".tmp")
    fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(values,f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,target)
    finally:
        tmp.unlink(missing_ok=True)
    return values
