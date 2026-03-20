import asyncio
import json
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Summarise API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _stream_sse(input: str, model: str, provider: str, theme: str):
    """Run the summarise pipeline and yield SSE events."""
    from .config import get_api_key, get_all_api_keys
    from .router import detect_input_type
    from .fetcher import fetch_url
    from .extractor import extract_content
    from .github import parse_github_url, fetch_repo_metadata, fetch_readme, fetch_tree, build_github_context
    from .youtube import fetch_metadata, fetch_transcript, build_youtube_context
    from .ai import stream_response, stream_response_with_fallback
    from .themes import get_theme_prompt
    from .chunker import chunk_text

    try:
        input_type = detect_input_type(input)
    except ValueError as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return

    yield f"data: {json.dumps({'status': 'detected', 'type': input_type})}\n\n"

    try:
        if input_type == "url":
            html = asyncio.run(fetch_url(input))
            content = extract_content(html, input)

        elif input_type == "youtube":
            metadata = fetch_metadata(input)
            yield f"data: {json.dumps({'status': 'metadata', 'title': metadata['title']})}\n\n"
            transcript = fetch_transcript(input)
            if transcript:
                content = build_youtube_context(metadata, transcript)
            else:
                content = f"Title: {metadata['title']}\nDescription: {metadata.get('description', '')[:1000]}"

        elif input_type == "github":
            owner, repo = parse_github_url(input)
            metadata = fetch_repo_metadata(owner, repo)
            yield f"data: {json.dumps({'status': 'metadata', 'name': metadata['name']})}\n\n"
            readme = fetch_readme(owner, repo)
            tree = fetch_tree(owner, repo, metadata['default_branch'])
            content = build_github_context(metadata, readme, tree)

        else:
            yield f"data: {json.dumps({'error': f'Unsupported input type for browser: {input_type}'})}\n\n"
            return

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return

    yield f"data: {json.dumps({'status': 'summarising'})}\n\n"

    try:
        api_key = get_api_key(provider)
    except SystemExit:
        api_key = None

    all_keys = get_all_api_keys()
    if not api_key and not all_keys:
        yield f"data: {json.dumps({'error': 'No API keys configured'})}\n\n"
        return

    theme_prompt = get_theme_prompt(theme)
    chunks = chunk_text(content)
    text = chunks[0] if len(chunks) == 1 else content

    try:
        if api_key:
            from .providers import create_provider
            prov = create_provider(provider, api_key)
            for token in prov.stream(text, model, system_prompt=theme_prompt):
                yield f"data: {json.dumps({'token': token})}\n\n"
        else:
            for token in stream_response_with_fallback(text, all_keys, preferred=provider, system_prompt=theme_prompt):
                yield f"data: {json.dumps({'token': token})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return

    yield f"data: {json.dumps({'status': 'done'})}\n\n"


@app.get("/summarise")
def summarise_endpoint(
    url: str = Query(..., description="URL to summarise"),
    model: str = Query("llama-3.3-70b-versatile", description="Model"),
    provider: str = Query("groq", description="Provider"),
    theme: str = Query("default", description="Theme"),
):
    return StreamingResponse(
        _stream_sse(url, model, provider, theme),
        media_type="text/event-stream",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


def start_server(host: str = "127.0.0.1", port: int = 11919):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
