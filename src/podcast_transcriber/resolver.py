from __future__ import annotations

from podcast_transcriber.models import Episode
from podcast_transcriber.resolvers.direct_audio import (
    is_direct_audio_url,
    resolve_direct_audio,
)
from podcast_transcriber.resolvers.xiaoyuzhou import is_xiaoyuzhou_url


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
