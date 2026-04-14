from __future__ import annotations

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


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = getattr(value, "get_text", lambda **_: "")(strip=True)
    return text or None
