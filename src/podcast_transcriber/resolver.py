from __future__ import annotations

import httpx

from podcast_transcriber.models import Episode
from podcast_transcriber.resolvers.direct_audio import (
    is_direct_audio_url,
    resolve_direct_audio,
)
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

    if is_xiaoyuzhou_url(url):
        response = httpx.get(
            url,
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "Mozilla/5.0 podcast-transcriber-cli"},
        )
        response.raise_for_status()
        return parse_episode_page(response.text, source_url=url)

    raise ResolverError(
        "Unsupported podcast URL. Try a Xiaoyuzhou public episode URL, RSS feed URL, Apple Podcasts URL, or direct audio file URL."
    )
