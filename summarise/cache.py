import hashlib
import json
from pathlib import Path

CACHE_DIR=Path.home()/ ".cache"/"summarise"


def cache_key(filepath:str)->str:
     
    p=Path(filepath)
    stat=p.stat()
    raw=f"{p.resolve()}:{stat.st_size}:{stat.st_mtime}"
    return hashlib.sha256(raw.encode()).hexdigest()
    

def get_cached_transcription(filepath:str)->str|None:
    """Return cached transcription if exists"""
    CACHE_DIR.mkdir(parents=True,exist_ok=True)
    cache_file=CACHE_DIR/f"{_cache_key(filepath)}.json"
    if cache_file.exists():
        data=json.loads(cache_file.read_text(encoding="utf-8"))
        return data.get("transcription")
    return None


def save_transcription(filepath:str,text:str):
     """Save transcription to cache"""
     CACHE_DIR.mkdir(parents=True,exist_ok=True)
     cache_file=CACHE_DIR/f"{_cache_key(filepath)}.json"
     cahce_file.write_text(
        json.dumps({"source":filepath,"text":text}),
        encoding="utf-8",
     )