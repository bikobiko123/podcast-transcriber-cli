from __future__ import annotations

from typing import Any

import feedparser

from podcast_transcriber.models import Episode


def parse_rss_items(xml: str, source_url: str) -> list[Episode]:
    parsed = feedparser.parse(xml)
    episodes: list[Episode] = []

    for entry in parsed.entries:
        audio_url = _extract_enclosure_url(entry)
        if not audio_url:
            continue
        episodes.append(
            Episode(
                source_url=getattr(entry, "link", source_url),
                audio_url=audio_url,
                title=getattr(entry, "title", "Untitled Episode"),
                platform="rss",
                description=getattr(entry, "summary", ""),
                published_at=getattr(entry, "published", None),
            )
        )

    return episodes


def _extract_enclosure_url(entry: Any) -> str | None:
    for link in getattr(entry, "links", []):
        href = link.get("href")
        link_type = link.get("type", "")
        rel = link.get("rel", "")
        if href and (rel == "enclosure" or link_type.startswith("audio/")):
            return href
    return None
