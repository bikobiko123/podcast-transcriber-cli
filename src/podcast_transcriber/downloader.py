from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

import httpx


def audio_filename_from_url(url: str, fallback: str = "audio.mp3") -> str:
    parsed = urlparse(url)
    name = PurePosixPath(unquote(parsed.path)).name or fallback
    stem = Path(name).stem.lower()
    suffix = Path(name).suffix.lower() or Path(fallback).suffix
    safe_stem = re.sub(r"[^\w\u4e00-\u9fff]+", "-", stem).strip("-") or "audio"
    return f"{safe_stem}{suffix}"


def download_audio(audio_url: str, tmp_dir: Path) -> Path:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    output_path = tmp_dir / audio_filename_from_url(audio_url)

    with httpx.stream("GET", audio_url, follow_redirects=True, timeout=None) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_bytes():
                if chunk:
                    handle.write(chunk)

    return output_path
