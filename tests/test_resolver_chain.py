import pytest

from podcast_transcriber.resolver import ResolverError, resolve_episode_from_known_inputs


def test_resolver_chain_accepts_direct_audio() -> None:
    episode = resolve_episode_from_known_inputs("https://cdn.example.com/a.mp3")
    assert episode.platform == "direct_audio"


def test_resolver_chain_rejects_unknown_url() -> None:
    with pytest.raises(ResolverError, match="Unsupported podcast URL"):
        resolve_episode_from_known_inputs("https://example.com/not-a-podcast")
