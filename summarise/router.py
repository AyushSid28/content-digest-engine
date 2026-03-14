import sys
from pathlib import Path
from .youtube import is_youtube_url
from .github import is_github_url
from .transcriber import is_audio_file
from .podcast import is_podcast_url

def detect_input_type(input: str) -> str:
    if input == "-":
        return "stdin"

    if input.startswith(("http://", "https://")):
        if is_youtube_url(input):
            return "youtube"
        if is_github_url(input):
            return "github"
        if is_podcast_url(input):
            return "podcast"
        return "url"

    if Path(input).exists():
        if is_audio_file(input):
            return 
        return "file"

    raise ValueError(
        f"Input '{input}' is not a valid URL, file or stdin"
    )

def detect_file_type(input: str) -> str:
    suffix = Path(input).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in (".txt", ".md", ".markdown", ".text"):
        return "text"
    return "text"