from __future__ import annotations

import httpx

from podcast_transcriber.models import Episode
from podcast_transcriber.resolvers.apple import is_apple_podcasts_url
from podcast_transcriber.resolvers.direct_audio import (
    is_direct_audio_url,
    resolve_direct_audio,
)
from podcast_transcriber.resolvers.rss import parse_rss_items
from podcast_transcriber.resolvers.xiaoyuzhou import (
    is_xiaoyuzhou_url,
    parse_episode_page,
)


class ResolverError(RuntimeError):
    pass


def resolve_episode_from_known_inputs(url: str) -> Episode:
    if is_direct_audio_url(url):
        return resolve_direct_audio(url)

    if is_xiaoyuzhou_url(url):
        raise ResolverError(
            "Xiaoyuzhou URL requires network resolution. Use resolve_episode(url) in the CLI pipeline."
        )

    raise ResolverError(
        "Unsupported podcast URL. Try a Xiaoyuzhou public episode URL, RSS feed URL, Apple Podcasts URL, or direct audio file URL."
    )


def resolve_episode(url: str) -> Episode:
    if is_direct_audio_url(url):
        return resolve_direct_audio(url)

    if is_apple_podcasts_url(url):
        raise ResolverError(
            "Apple Podcasts pages are recognized but not resolved in v0.1. "
            "Use the podcast RSS feed URL or a direct audio URL for now."
        )

    if is_xiaoyuzhou_url(url):
        return parse_episode_page(_fetch_text(url), source_url=url)

    episodes = parse_rss_items(_fetch_text(url), source_url=url)
    if episodes:
        return episodes[0]

    raise ResolverError(
        "Unsupported podcast URL. Try a Xiaoyuzhou public episode URL, RSS feed URL, or direct audio file URL."
    )


def _fetch_text(url: str) -> str:
    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=30.0,
        headers={"User-Agent": "Mozilla/5.0 podcast-transcriber-cli"},
    )
    response.raise_for_status()
    return response.text
