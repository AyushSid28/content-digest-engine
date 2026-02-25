# summarize

> Point at any URL or file. Get the gist.

## Overview

| Field | Details |
|-------|---------|
| **GitHub** | [steipete/summarize](https://github.com/steipete/summarize) |
| **Stars** | 4,422 |
| **Original Language** | TypeScript |
| **Our Language** | Python |
| **Complexity** | High |
| **Category** | Content Summarizer |

## What It Does

A CLI and Chrome/Firefox extension that produces fast summaries from URLs, files, YouTube videos, podcasts, PDFs, images, and audio/video. Supports streaming Markdown output, multiple AI providers, slide extraction with OCR, and a local daemon for the browser extension.

## Key Features

- **Universal input**: URLs, files, PDFs, images, audio/video, YouTube, podcasts
- **Browser extension**: Chrome Side Panel + Firefox Sidebar with streaming chat
- **YouTube slides**: OCR + timestamped cards extraction
- **Multi-provider**: OpenAI, Groq (free Llama/Mixtral), OpenRouter free models
- **Auto model selection**: With fallback chains
- **Whisper transcription**: Local whisper via `openai-whisper` or Groq Whisper API (free)
- **Free tier**: Via Groq free models + OpenRouter `:free` models
- **Pipe/stdin support**: JSON output, configurable themes

## Tech Stack (Python Build)

| Component | Library |
|-----------|---------|
| **Language** | Python 3.11+ |
| **CLI Framework** | `click` or `typer` |
| **HTTP Client** | `httpx` (async support) |
| **Web Scraping** | `beautifulsoup4` + `trafilatura` (article extraction) |
| **YouTube** | `yt-dlp` (download/extract info) |
| **PDF Parsing** | `PyPDF2` or `pdfplumber` |
| **AI - Groq** | `groq` (free tier — Llama 3.3 70B, Mixtral) |
| **AI - OpenAI** | `openai` (your existing key) |
| **Transcription** | `openai-whisper` (local) or Groq Whisper API (free) |
| **OCR** | `pytesseract` + `Pillow` |
| **Rich Output** | `rich` (Markdown rendering in terminal) |
| **Testing** | `pytest` |
| **Packaging** | `pyproject.toml` + `setuptools` |

## Why It's Interesting

A Swiss Army knife for content digestion. The breadth of supported inputs (URLs, YouTube, podcasts, PDFs, audio) combined with multi-provider fallback makes it incredibly versatile. Building this teaches you web scraping, AI API integration, and content processing pipelines.

## Build Complexity Assessment

- **High** — Handles dozens of content types, multiple AI providers, transcription pipelines
- Excellent learning project covering many Python skills
- Could be built incrementally (start with URL summaries, add formats over time)

## Build Plan

1. Start with URL summarization (requests + beautifulsoup4 + Groq)
2. Add file/PDF support (PyPDF2)
3. Add YouTube (yt-dlp + transcript extraction)
4. Add audio transcription (whisper)
5. Add rich terminal output (rich markdown)
6. Add multi-provider fallback (Groq -> OpenAI)
