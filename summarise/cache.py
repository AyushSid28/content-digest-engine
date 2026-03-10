import hashlib
import json
from pathlib import Path

CACHE_DIR=Path.home()/ ".cache"/"summarise"


def cache_key(filepath:str)->str:
     
    p=Path(filepath)
    stat=p.stat()
    raw=f"{p.resolve()}:{stat.st_size}:{stat.st_mtime}"
    return hashlib.sha256(raw.encode()).hexdigest()