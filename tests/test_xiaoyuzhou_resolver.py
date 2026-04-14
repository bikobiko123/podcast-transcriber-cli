from pathlib import Path

from podcast_transcriber.resolvers.xiaoyuzhou import (
    is_xiaoyuzhou_url,
    parse_episode_page,
)


def test_is_xiaoyuzhou_url() -> None:
    assert is_xiaoyuzhou_url("https://www.xiaoyuzhoufm.com/episode/65abc")
    assert not is_xiaoyuzhou_url("https://example.com/demo.mp3")


def test_parse_episode_page_extracts_open_graph_audio() -> None:
    html = Path("tests/fixtures/xiaoyuzhou/episode_page.html").read_text(
        encoding="utf-8"
    )
    episode = parse_episode_page(
        html,
        source_url="https://www.xiaoyuzhoufm.com/episode/65abc",
    )
    assert episode.platform == "xiaoyuzhou"
    assert episode.title == "Demo Xiaoyuzhou Episode"
    assert episode.audio_url == "https://media.example.com/xiaoyuzhou-demo.m4a"
