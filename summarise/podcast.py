import re
import tempfile
from pathlib import Path
import httpx
from xml.etree import ElementTree

PODCAST_PATTERNS=[
    re.compile(r"\.mp3(\?.*)?$",re.IGNORECASE),
    re.compile(r"feed|rss|podcast",re.IGNORECASE),
    re.compile(r"/episodes?/",re.IGNORECASE),
]


def is_podcast_url(url:str)->bool:
    """Detect if a URL  looks like a podcast feed or episode"""
    if any(p.search(url) for p in PODCAST_PATTERNS):
        return True
    return False


def fetch_podcast_audio(url:str)->str:
    """Download podcast audio from a direct URL"""
    if _is_direct_audio(url):
        return _download_audio(url)
    return _download_from_feed(url)


def _is_direct_audio(url:str)->bool:
  return bool(re.search(r"\.(mp3|m4a|ogg|wav|aac)(\?.*)?$",url,re.IGNORECASE))

def _download_audio(url:str)->str:
    """Download audio from a direct url to a temp file"""
    resp=httpx.get(url,follow_redirects=True,timeout=30.0)
    resp.raise_for_status()
    suffix=".mp3"
    match = re.search(r"\.(mp3|m4a|ogg|wav|aac)", url, re.IGNORECASE)
    if match:
        suffix=f".{match.group(1).lower()}"
    tmp=tempfile.NamedTemporaryFile(suffix=suffix,delete=False)
    tmp.write(resp.content)
    tmp.close()
    return tmp.name

def _download_from_feed(url:str)->str:
    """Parse RSS,feed,find latest episode and download it"""
    resp=httpx.get(url,follow_redirects=True,timeout=30.0)
    resp.raise_for_status()
    try:
        root=ElementTree.fromstring(resp.text)
    except ElementTree.ParseError:
        raise ValueError(f"Could not parse RSS feed: {url}")


    for enclosure in root.iter("enclosure"):
        audio_url=enclosure.get("url","")
        audio_type=enclosure.get("type","")
        if "audio" in audio_type or _is_direct_audio(audio_url):
            return _download_audio(audio_url)

    raise ValueError(f"No audio enclosure foundin feed {url}")

