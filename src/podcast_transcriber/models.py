from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Episode:
    source_url: str
    audio_url: str
    title: str
    platform: str
    description: str = ""
    published_at: str | None = None


@dataclass(frozen=True)
class Transcript:
    text: str
    language: str
    duration_seconds: float | None
    model: str
    backend: str = "faster-whisper"
