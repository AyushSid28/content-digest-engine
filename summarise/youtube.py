import re
import json
import tempfile
import subprocess
from pathlib import Path


YOUTUBE_PATTERNS=[
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]+)"),
    re.compile(r"(?:https?://)?youtu\.be/([\w-]+)"),
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]+)"),
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([\w-]+)"),
]


def is_youtube_url(url:str)->bool:
    return any(p.search(url) for p in YOUTUBE_PATTERNS)


def get_video_id(url:str)->str:
    for p in YOUTUBE_PATTERNS:
        match=p.search(url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from {url}")

#Pull the metadata like title,channel,duration,description using yt-dlp
def fetch_metadata(url:str)->dict:
    result=subprocess.run(
        ["yt-dlp","--dump-json","--no-download",url],
        capture_output=True,text=True,timeout=30,

    )
    if result.returncode!=0:
       raise RuntimeError(f"yt-dlp metadata failed: {result.stderr.strip()}")

    data=json.loads(result.stdout)

    return{
        "title":data.get("title",""),
        "channel":data.get("channel",data.get("uploader","")),
        "duration":data.get("duration",0),
        "description":data.get("description",""),
    }

#Extract subtitles/transcript using yt-dlp returning text or None
def fetch_transcript(url:str)->str|None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path=Path(tmpdir)/"subs"
        result=subprocess.run(
            [
                "yt-dlp",
                "--write-subs","--write-auto-subs",
                "--sub-lang","en",
                "--sub-format","vtt",
                "--skip-download",
                "-o",str(out_path),
                url,
            ],
            capture_output=True,text=True,timeout=60,
        )

        vtt_files=list(Path(tmpdir).glob("*.vtt"))
        if not vtt_files:
            return None
        return _parse_vtt(vtt_files[0])

def _parse_vtt(vtt_path:Path)->str:
    lines=vtt_path.read_text(encoding="utf-8").splitlines()
    entries=[]
    current_time=""
    current_text=[]
    seen=set()

    for line in lines:
        line=line.strip()
        if "-->" in line:
            if current_text:
                text=" ".join(current_text).strip()
                if text not in seen:
                    entries.append(f"[{current_time}] {text}")
                    seen.add(text)

            current_time=line.split("-->")[0].strip()
            current_text=[]
        elif line and not line.startswith("WEBVTT") and not line.startswith("Kind:") and not line.startswith("Language:") and not line.isdigit():
            cleaned=re.sub(r"<[^>]+>", "", line)
            if cleaned.strip():
                current_text.append(cleaned.strip())

    if current_text:
        text=" ".join(current_text)
        if text not in seen:
            entries.append(f"[{current_time}] {text}")

    return "\n".join(entries)


def download_audio(url:str,output_dir:str="/tmp") ->str:
    out_path=Path(output_dir)/"%(id)s.%(ext)s"
    result=subprocess.run(
        [
            "yt-dlp",
            "-x","--audio-format","mp3",
            "-o",str(out_path),
            url,

        ],
        capture_output=True,text=True,timeout=300,
    )
    if result.returncode!=0:
        raise RuntimeError(f"Audio download failed:{result.stderr.strip()}")
    video_id=get_video_id(url)
    mp3_path=Path(output_dir)/f"{video_id}.mp3"
    if not mp3_path.exists():
        candidates=list(Path(output_dir).glob(f"{video_id}.*"))
        if candidates:
            return str(candidates[0])
        raise FileNotFoundError(f"Downloaded audio not found at {video_id}")
    return str(mp3_path)


def format_duration(seconds:int)->str:
    h, remainder=divmod(seconds,3600)
    m, s=divmod(remainder,60)
    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def build_youtube_context(metadata:dict,transcript:str)-> str:
    duration=format_duration(metadata["duration"]) if metadata["duration"] else "unknown"
    header=(
        f"Title: {metadata['title']}\n"
        f"Channel: {metadata['channel']}\n"
        f"Duration: {duration}\n"
    )
    if metadata["description"]:
        desc=metadata["description"][:500]
        header+=f"Description: {desc}\n"
    header +=f"\n-- Transcript --\n{transcript}"
    return header