from __future__ import annotations

from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

from podcast_transcriber.models import Episode


AUDIO_EXTENSIONS = (".mp3", ".m4a", ".wav", ".aac", ".ogg", ".wma", ".flac")


def is_direct_audio_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()
    return parsed.scheme in {"http", "https"} and path.endswith(AUDIO_EXTENSIONS)


def resolve_direct_audio(url: str) -> Episode:
    parsed = urlparse(url)
    stem = PurePosixPath(unquote(parsed.path)).stem or "audio"
    return Episode(
        source_url=url,
        audio_url=url,
        title=stem,
        platform="direct_audio",
    )
