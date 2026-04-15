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
/Users/bikodemac/Desktop/code-workspace/biko 仓库-真/00_收件箱/<episode-title>.md
tmp/<downloaded-audio>  # deleted after processing
```

If the output directory does not exist, the CLI asks before creating it. Use
`--output-dir` or `TRANSCRIPT_DIR` to override the default location.

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
- On Apple Silicon, install the optional MLX backend for faster local inference:

```bash
python -m pip install -e ".[mlx]"
podcast-transcribe "https://www.xiaoyuzhoufm.com/episode/..." --backend mlx --language zh
```

The default backend is `faster-whisper` for cross-platform compatibility. MLX
model names like `tiny`, `base`, `small`, `medium`, `large-v3`, and `turbo` map
to `mlx-community/whisper-*-mlx` repositories. You can also pass a full
`mlx-community/...` model repo or a local model path with `--model`. The CLI
loads audio through PyAV before calling MLX, so it does not need a system
`ffmpeg` binary for the MLX path.

MLX troubleshooting:

- `python -m pip install -e ".[mlx]"` follows the official `mlx-whisper`
  dependency metadata, which may download large packages including `torch`.
- For a smaller Apple Silicon setup, this project has also been verified with:

```bash
python -m pip install mlx-whisper==0.4.3 --no-deps
python -m pip install "mlx>=0.11" numba scipy tiktoken more-itertools
```

- MLX needs Apple Metal access. If an agent shell sandbox crashes while importing
  `mlx.core`, rerun the command in a local or escalated shell.

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
