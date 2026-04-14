---
name: podcast-transcriber
description: Use when the user asks to transcribe or summarize a podcast episode from Xiaoyuzhou, RSS, Apple Podcasts, or a direct audio URL using the local podcast-transcribe CLI.
---

# Podcast Transcriber

Use this skill when the user wants a podcast link turned into Markdown transcript notes.

## Workflow

1. Confirm the repository is installed or locate the `podcast-transcribe` command.
2. Prefer this command when no API key is known:

```bash
podcast-transcribe "<URL>" --summary agent
```

3. If the user explicitly wants automatic API summaries and API credentials are configured, use:

```bash
podcast-transcribe "<URL>" --summary api
```

4. After the command completes, read the generated Markdown path printed after `Done:`.
5. If the Markdown contains `## Summary Prompt`, fill the `## Summary` section using the transcript and preserve the transcript unchanged.
6. Report the generated file path and any warnings.

## Defaults

- Xiaoyuzhou public episode links are the preferred and strongest supported path.
- Default Faster-Whisper model is `small`.
- Transcript files are written to `transcripts/`.
- Temporary audio files are written to `tmp/` and deleted after processing.
