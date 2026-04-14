from __future__ import annotations

import json
from collections.abc import Iterable

from bs4 import BeautifulSoup

from podcast_transcriber.models import Episode


def is_xiaoyuzhou_url(url: str) -> bool:
    return "xiaoyuzhoufm.com/episode/" in url


def parse_episode_page(html: str, source_url: str) -> Episode:
    soup = BeautifulSoup(html, "html.parser")
    title = (
        _meta_content(soup, "og:title")
        or _text(soup.find("h1"))
        or "Xiaoyuzhou Episode"
    )
    description = _meta_content(soup, "og:description") or ""
    audio_url = (
        _meta_content(soup, "og:audio")
        or _json_ld_audio(soup)
        or _next_data_audio(soup)
        or _meta_content(soup, "music:preview_url")
        or _first_audio_source(soup)
    )
    if not audio_url:
        raise ValueError(
            "Could not find a public audio URL on this Xiaoyuzhou episode page"
        )
    return Episode(
        source_url=source_url,
        audio_url=audio_url,
        title=title,
        platform="xiaoyuzhou",
        description=description,
    )


def _meta_content(soup: BeautifulSoup, property_name: str) -> str | None:
    tag = soup.find("meta", attrs={"property": property_name})
    if tag and tag.get("content"):
        return str(tag["content"]).strip()
    return None


def _first_audio_source(soup: BeautifulSoup) -> str | None:
    for tag in soup.find_all(["audio", "source"]):
        src = tag.get("src")
        if src:
            return str(src).strip()
    return None


def _json_ld_audio(soup: BeautifulSoup) -> str | None:
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        data = _parse_json(_text(tag) or "")
        for candidate in _find_values(data, "contentUrl"):
            if _looks_like_audio_url(candidate):
                return candidate
    return None


def _next_data_audio(soup: BeautifulSoup) -> str | None:
    tag = soup.find("script", attrs={"id": "__NEXT_DATA__"})
    data = _parse_json(_text(tag) if tag else "")
    for candidate in _find_values(data, "url"):
        if _looks_like_audio_url(candidate):
            return candidate
    return None


def _parse_json(value: str) -> object | None:
    if not value.strip():
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _find_values(value: object, key: str) -> Iterable[str]:
    if isinstance(value, dict):
        for dict_key, dict_value in value.items():
            if dict_key == key and isinstance(dict_value, str):
                yield dict_value.strip()
            yield from _find_values(dict_value, key)
    elif isinstance(value, list):
        for item in value:
            yield from _find_values(item, key)


def _looks_like_audio_url(value: str) -> bool:
    lower_value = value.lower()
    return lower_value.startswith(("http://", "https://")) and any(
        extension in lower_value
        for extension in (".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac")
    )


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = getattr(value, "get_text", lambda **_: "")(strip=True)
    return text or None
