---
name: podcast-transcriber
description: Use when the user asks to transcribe or summarize a podcast episode from Xiaoyuzhou, an RSS feed, or a direct audio URL using the local podcast-transcribe CLI.
---

# Podcast Transcriber

Use this skill when the user wants a podcast link turned into Markdown transcript notes.

## Workflow

1. Confirm the repository is installed or locate the `podcast-transcribe` command.
2. Prefer this command when no API key is known:

```bash
podcast-transcribe "<URL>" --summary agent
```

3. On Apple Silicon, prefer the MLX backend when it is installed and speed matters:

```bash
podcast-transcribe "<URL>" --backend mlx --language zh --summary agent
```

Run MLX commands in a local or escalated shell if the agent sandbox blocks Apple
Metal access.

4. If the user explicitly wants automatic API summaries and API credentials are configured, use:

```bash
podcast-transcribe "<URL>" --summary api
```

5. After the command completes, read the generated Markdown path printed after `Done:`.
6. If the Markdown contains `## Summary Prompt`, fill the `## Summary` section using the transcript and preserve the transcript unchanged.
7. Report the generated file path and any warnings.

## Defaults

- Xiaoyuzhou public episode links are the preferred and strongest supported path.
- RSS feed URLs and direct audio URLs are also supported.
- Apple Podcasts pages are recognized but need the RSS feed URL or direct audio URL in v0.1.
- Default Faster-Whisper model is `small`.
- Optional MLX backend is available with `--backend mlx` after installing `.[mlx]`.
- MLX loads audio through PyAV, so it does not need a system `ffmpeg` binary.
- Transcript files are written to `transcripts/`.
- Temporary audio files are written to `tmp/` and deleted after processing.

## Troubleshooting

- If `.[mlx]` installation is slow, it is usually downloading large optional
  packages from `mlx-whisper` dependency metadata.
- A smaller Apple Silicon setup can install:

```bash
python -m pip install mlx-whisper==0.4.3 --no-deps
python -m pip install "mlx>=0.11" numba scipy tiktoken more-itertools
```

- If importing `mlx.core` crashes inside a sandbox, retry outside the sandbox or
  request an escalated shell command so MLX can access Metal.
