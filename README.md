# Podcast Transcriber CLI

Local-first podcast transcription CLI with a Xiaoyuzhou-first resolver, RSS feed support, and direct audio URL support.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
podcast-transcribe "https://www.xiaoyuzhoufm.com/episode/..."
```

The default Whisper model is `small`.

## Usage

```bash
podcast-transcribe "https://www.xiaoyuzhoufm.com/episode/..." --summary agent
```

Output:

```text
transcripts/<episode-title>.md
tmp/<downloaded-audio>  # deleted after processing
```

Summary modes:

- `auto`: use API summary when `OPENAI_API_KEY` exists, otherwise write a prompt
- `agent`: always write a prompt for Codex or Claude Code to complete
- `api`: require OpenAI-compatible API settings
- `off`: transcript only

Transcription progress is printed every 5%. The CLI defaults to a CPU-friendly
fast decode path: `--beam-size 1`, `best_of=1`, no temperature fallback, and no
previous-text conditioning. Raise `--beam-size` only when you want slower, more
exhaustive decoding.

Speed tips:

- Add `--language zh` for Chinese episodes to skip language detection.
- Use `--model base` or `--model tiny` when speed matters more than accuracy.
- Keep `--model small` for a better quality/speed balance on CPU.
- On Apple Silicon, an MLX backend is the likely next major speed upgrade.

Supported inputs:

- Xiaoyuzhou public episode links: strongest v0.1 path
- RSS feed URLs: resolves the first audio enclosure in the feed
- Direct audio URLs: `.mp3`, `.m4a`, `.wav`, `.aac`, `.ogg`, `.wma`, `.flac`
- Apple Podcasts pages: recognized with a clear error; use the RSS feed URL or direct audio URL for now

If Hugging Face model downloads are unstable on your network, pre-cache the
model through a mirror:

```bash
HF_ENDPOINT=https://hf-mirror.com .venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-small', max_workers=1)"
```

## Agent Skill

This repository includes a skill wrapper at `skills/podcast-transcriber/SKILL.md`.

For Codex or Claude Code, copy or symlink that folder into your agent skills directory, then ask the agent to transcribe a podcast link. The skill will call `podcast-transcribe` and, when needed, fill the structured summary from the generated transcript.
