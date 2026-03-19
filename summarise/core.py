import asyncio
from typing import Optional
from .config import get_api_key, get_all_api_keys
from .fetcher import fetch_url
from .extractor import extract_content
from .ai import stream_response, stream_response_with_fallback
from .output import render_markdown, console
from .router import detect_file_type, detect_input_type
from .reader import read_text_file, read_pdf, read_stdin
from .chunker import chunk_text, merge_summary
from .youtube import fetch_metadata, fetch_transcript, download_audio, build_youtube_context
from .github import parse_github_url, fetch_repo_metadata, fetch_readme, fetch_tree, build_github_context
from .transcriber import transcribe
from .podcast import fetch_podcast_audio
from .ocr import process_image


def summarise_pipeline(
    input: str, model: str, provider: str,
    output: Optional[str] = None, timestamps: bool = False,
):
    """Pipeline: detect input -> get content -> summarise -> display."""
    try:
        input_type = detect_input_type(input)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    console.print(f"[bold]Input type:[/bold] {input_type}")

    try:
        api_key = get_api_key(provider)
    except SystemExit:
        api_key = None

    all_keys = get_all_api_keys()
    if not api_key and not all_keys:
        console.print("[red]No API keys configured. Set at least one in your .env file.[/red]")
        raise SystemExit(1)

    groq_key = api_key if provider == "groq" else all_keys.get("groq")

    try:
        if input_type == "url":
            console.print(f"[bold]Fetching:[/bold] {input} ...")
            html = asyncio.run(fetch_url(input))
            content = extract_content(html, input)

        elif input_type == "youtube":
            console.print(f"[bold]Fetching YouTube video:[/bold] {input}")
            metadata = fetch_metadata(input)
            console.print(f"[bold]Title:[/bold] {metadata['title']}")
            console.print(f"[bold]Channel:[/bold] {metadata['channel']}")

            transcript = fetch_transcript(input)
            if transcript:
                console.print("[bold]Transcript found[/bold]")
                content = build_youtube_context(metadata, transcript)
            else:
                console.print("[yellow]No transcript — downloading audio for Whisper[/yellow]")
                audio_path = download_audio(input)
                console.print("[bold]Transcribing audio...[/bold]")
                content = transcribe(audio_path, api_key=groq_key)

            if timestamps:
                content = "[Instruction: Include timestamps in your summary]\n\n" + content

        elif input_type == "github":
            console.print(f"[bold]Fetching GitHub repo:[/bold] {input}")
            owner, repo = parse_github_url(input)
            metadata = fetch_repo_metadata(owner, repo)
            console.print(f"[bold]{metadata['name']}[/bold] — {metadata['description']}")
            console.print(f"[dim]{metadata['language']} | Stars: {metadata['stars']} | Forks: {metadata['forks']}[/dim]")

            readme = fetch_readme(owner, repo)
            tree = fetch_tree(owner, repo, metadata['default_branch'])
            content = build_github_context(metadata, readme, tree)

        elif input_type == "audio":
            console.print(f"[bold]Transcribing audio:[/bold] {input} ...")
            content = transcribe(input, api_key=groq_key)
            console.print("[bold]Transcription complete[/bold]")

        elif input_type == "podcast":
            console.print(f"[bold]Downloading podcast audio:[/bold] {input} ...")
            audio_path = fetch_podcast_audio(input)
            console.print("[bold]Transcribing...[/bold]")
            content = transcribe(audio_path, api_key=groq_key)
            console.print("[bold]Transcription complete[/bold]")

        elif input_type == "image":
            console.print(f"[bold]Processing image:[/bold] {input} ...")
            vision_key = all_keys.get("openai")
            content = process_image(input, api_key=vision_key, vision_provider="openai" if vision_key else None)
            console.print("[bold]Image processed[/bold]")

        elif input_type == "file":
            file_type = detect_file_type(input)
            console.print(f"[bold]Reading {file_type}:[/bold] {input} ...")
            if file_type == "pdf":
                content = read_pdf(input)
            else:
                content = read_text_file(input)

        elif input_type == "stdin":
            console.print("[bold]Reading from stdin...[/bold]")
            content = read_stdin()

    except Exception as e:
        console.print(f"[red]Error reading input:[/red] {e}")
        raise SystemExit(1)

    chunks = chunk_text(content)

    def _summarise(text: str):
        if api_key:
            return stream_response(text, api_key, model, provider_name=provider)
        return stream_response_with_fallback(text, all_keys, model=None, preferred=provider)

    if len(chunks) == 1:
        console.print(f"[bold]Summarising with {provider}/{model}...[/bold]\n")
        try:
            render_markdown(_summarise(chunks[0]), output)
        except Exception as e:
            console.print(f"[red]Error during summarisation:[/red] {e}")
            raise SystemExit(1)
    else:
        console.print(f"[bold]Large document — summarising {len(chunks)} chunks...[/bold]\n")
        try:
            partial_summaries = []
            for i, chunk in enumerate(chunks, 1):
                console.print(f"[dim]  Chunk {i}/{len(chunks)}...[/dim]")
                full = ""
                for token in _summarise(chunk):
                    full += token
                partial_summaries.append(full)

            merged = merge_summary(partial_summaries)
            console.print("[bold]Merging into final summary...[/bold]\n")
            render_markdown(
                _summarise(f"Combine these partial summaries into one cohesive summary:\n\n{merged}"),
                output,
            )
        except Exception as e:
            console.print(f"[red]Error during summarisation:[/red] {e}")
            raise SystemExit(1)
