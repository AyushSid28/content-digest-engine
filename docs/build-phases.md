# Summarise — Build Phases

> Python port of [steipete/summarize](https://github.com/steipete/summarize). Phased plan from zero to full-featured CLI.

---

## Phase 1 — Foundation & URL Summarization (Core MVP)

**Goal:** A working CLI that takes a URL, extracts the page content, sends it to Groq, and prints a summary.

| Task | Details |
|------|---------|
| Project scaffolding | Set up `pyproject.toml`, proper package structure (`summarise/`), entry point |
| CLI skeleton | Use `typer` for the CLI — `summarise <input>` with flags like `--model`, `--provider`, `--output` |
| URL fetching | Fetch page HTML with `httpx` (async) |
| Content extraction | Use `trafilatura` (primary) with `beautifulsoup4` fallback to extract article text from raw HTML |
| AI summarization | Send extracted text to **Groq** (Llama 3.3 70B free tier) and stream the response |
| Terminal output | Use `rich` to render the streamed Markdown summary in the terminal |
| Config & API keys | `.env` file support for `GROQ_API_KEY`, basic config loading |
| Error handling | Graceful handling of bad URLs, network errors, empty content, API failures |

**Deliverable:** `summarise https://example.com/article` prints a rich Markdown summary.

---

## Phase 2 — File & PDF Support

**Goal:** Expand input types to local files and PDFs.

| Task | Details |
|------|---------|
| Input router | Detect whether the input is a URL, file path, or stdin — route accordingly |
| Plain text/Markdown files | Read and pass directly to the AI provider |
| PDF extraction | Use `pdfplumber` (better table/layout support) with `PyPDF2` as fallback |
| Token management | Chunk large documents to stay within model context limits; summarize chunks then merge |
| Stdin/pipe support | Allow `cat file.txt \| summarise -` for piped input |

**Deliverable:** `summarise ./paper.pdf` and `echo "text" | summarise -` both work.

---

## Phase 3 — YouTube & Video Support

**Goal:** Summarize YouTube videos using transcripts.

| Task | Details |
|------|---------|
| YouTube detection | Detect YouTube URLs (various formats: `youtu.be`, `youtube.com/watch`, etc.) |
| Transcript extraction | Use `yt-dlp` to extract auto-generated or manual subtitles/transcripts |
| Metadata enrichment | Pull video title, channel, duration, description for context |
| Fallback: audio download | If no transcript available, download audio for Phase 4's Whisper pipeline |
| Timestamped summaries | Optionally produce time-stamped section summaries |

**Deliverable:** `summarise https://youtube.com/watch?v=...` prints a structured summary with key points.

---

## Phase 3.5 — GitHub Repository Summarization

**Goal:** Summarize a GitHub repository by pulling its README, structure, and metadata.

| Task | Details |
|------|---------|
| GitHub URL detection | Detect `github.com/<owner>/<repo>` URLs (with or without trailing paths) |
| Repo metadata | Fetch repo description, stars, language, topics via GitHub REST API |
| README extraction | Fetch and parse the repo's README.md (raw content) |
| Directory tree | Fetch the repo file tree to show project structure |
| Tech stack detection | Identify tech stack from config files (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.) |
| Context assembly | Combine metadata + README + tree into a prompt-ready context |

**Deliverable:** `summarise https://github.com/owner/repo` prints a project overview with purpose, tech stack, and structure.

---

## Phase 4 — Audio Transcription (Whisper)

**Goal:** Transcribe and summarize audio/video files and podcast URLs.

| Task | Details |
|------|---------|
| Audio file detection | Support `.mp3`, `.wav`, `.m4a`, `.ogg`, etc. |
| Whisper integration | Local transcription via `openai-whisper` |
| Groq Whisper API | Alternative fast transcription using Groq's free Whisper API |
| Podcast URL support | Detect podcast RSS/episode URLs, download audio, transcribe |
| Transcription caching | Cache transcriptions locally to avoid re-processing |
| Pipeline: transcribe → summarize | Chain the transcription output into the summarization pipeline |

**Deliverable:** `summarise podcast.mp3` and `summarise <podcast-episode-url>` work end-to-end.

---

## Phase 5 — Multi-Provider AI & Fallback Chains

**Goal:** Support multiple AI providers with automatic fallback.

| Task | Details |
|------|---------|
| Provider abstraction | Create a unified interface for AI providers (Groq, OpenAI, OpenRouter) |
| OpenAI integration | Add `openai` SDK support with GPT-4o / GPT-4o-mini |
| OpenRouter integration | Add OpenRouter free models (`:free` suffix) |
| Auto model selection | Pick the best model based on input length, content type, and available API keys |
| Fallback chain | Groq → OpenRouter free → OpenAI; automatic retry on rate limits or failures |
| Provider config | User-configurable provider priority via CLI flags or config file |

**Deliverable:** Summarization works even if one provider is down; `--provider openai` overrides the default.

---

## Phase 6 — Image & OCR Support

**Goal:** Summarize images, slides, and scanned documents.

| Task | Details |
|------|---------|
| Image detection | Support `.png`, `.jpg`, `.webp`, `.tiff`, etc. |
| OCR pipeline | Use `pytesseract` + `Pillow` to extract text from images |
| YouTube slide extraction | Detect slide-heavy videos, extract key frames, OCR them |
| Timestamped slide cards | Pair OCR'd slide content with video timestamps |
| Vision API fallback | Optionally use GPT-4o vision or similar for image understanding |

**Deliverable:** `summarise screenshot.png` extracts and summarizes text; YouTube slide decks get structured output.

---

## Phase 7 — Polish, Packaging & Distribution

**Goal:** Production-quality CLI ready for distribution.

| Task | Details |
|------|---------|
| JSON output mode | `--json` flag for structured output (for piping to other tools) |
| Configurable themes | `--theme` for output styling (minimal, detailed, bullet-points) |
| Progress indicators | Rich progress bars for downloads, transcription, etc. |
| Comprehensive tests | `pytest` suite covering all input types, providers, edge cases |
| Documentation | README with install instructions, examples, provider setup guides |
| PyPI packaging | Publish to PyPI as an installable CLI (`pip install summarise`) |
| CI/CD | GitHub Actions for testing and automated publishing |

---

## Phase 8 (Stretch) — Browser Extension

**Goal:** Chrome/Firefox extension for one-click summarization.

| Task | Details |
|------|---------|
| Local daemon | A lightweight HTTP server (`FastAPI`/`Flask`) that the extension talks to |
| Chrome Side Panel | Extension with streaming chat interface |
| Firefox Sidebar | Firefox equivalent |
| Streaming responses | SSE or WebSocket for real-time summary streaming to the browser |

---

## Dependencies & Recommended Order

```
Phase 1 (URL) ──→ Phase 2 (Files/PDF) ──→ Phase 3 (YouTube)
                                               │
                                               ▼
                                          Phase 4 (Audio/Whisper)
                                               │
Phase 5 (Multi-Provider) can start anytime after Phase 1
Phase 6 (OCR/Images) depends on Phase 3 for YouTube slides
Phase 7 (Polish) runs continuously but finalizes last
Phase 8 (Browser Extension) is independent, start after Phase 1
```

Phase 1 is the critical path — everything else builds on its CLI skeleton, content pipeline, and AI integration. Tackle Phase 1 first, then move sequentially through 2→3→4, with Phase 5 (multi-provider) woven in whenever Groq's free tier rate limits become a bottleneck.
