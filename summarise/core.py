import asyncio
from typing import Optional
from .config import get_api_key
from .fetcher import fetch_url
from .extractor import extract_content
from .ai import stream_response
from .output import render_markdown,console
from .router import detect_file_type,detect_input_type
from .reader import read_text_file,read_pdf,read_stdin
from .chunker import chunk_text,merge_summary


def summarise_pipeline(input:str,model:str,provider:str,output:Optional[str]=None,):
    "PIPELINE: Fetch URL-> Extract Content->Summarise->Display"
    console.print(f"Fetching: {input} ...")

    try:
        input_type=detect_input_type(input)
    except Exception as e:
        console.print(f"Error Fetching URL:")
        raise SystemExit(1)

    console.print(f"Input Type: {input_type}")

    try:
        if input_type=="url":
            

