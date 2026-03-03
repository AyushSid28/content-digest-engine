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


