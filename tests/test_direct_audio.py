from podcast_transcriber.resolvers.direct_audio import (
    is_direct_audio_url,
    resolve_direct_audio,
)


def test_direct_audio_url_detects_common_extensions() -> None:
    assert is_direct_audio_url("https://cdn.example.com/a/show.m4a?token=1")
    assert is_direct_audio_url("https://cdn.example.com/a/show.mp3")
    assert not is_direct_audio_url("https://www.xiaoyuzhoufm.com/episode/abc")


def test_resolve_direct_audio_returns_episode() -> None:
    episode = resolve_direct_audio("https://cdn.example.com/folder/my-episode.mp3")
    assert episode.audio_url == "https://cdn.example.com/folder/my-episode.mp3"
    assert episode.platform == "direct_audio"
    assert episode.title == "my-episode"
