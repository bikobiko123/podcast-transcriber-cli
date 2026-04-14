from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from podcast_transcriber.models import Episode, Transcript


def safe_slug(value: str, fallback: str = "episode") -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or fallback


def write_markdown(
    episode: Episode,
    transcript: Transcript,
    output_dir: Path,
    summary_markdown: str,
    summary_mode: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{safe_slug(episode.title)}.md"
    output_path = output_dir / filename
    transcribed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    content = f'''---
title: "{episode.title}"
source_url: "{episode.source_url}"
platform: "{episode.platform}"
audio_url: "{episode.audio_url}"
transcribed_at: "{transcribed_at}"
whisper_model: "{transcript.model}"
language: "{transcript.language}"
summary_mode: "{summary_mode}"
---

# {episode.title}

## Source

- URL: {episode.source_url}
- Platform: {episode.platform}
- Audio URL: {episode.audio_url}

## Summary

{summary_markdown.strip()}

## Transcript

{transcript.text.strip()}
'''
    output_path.write_text(content, encoding="utf-8")
    return output_path
