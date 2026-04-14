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
