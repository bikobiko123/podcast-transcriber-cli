# Podcast Transcriber CLI

Local-first podcast transcription CLI with a Xiaoyuzhou-first resolver.

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
