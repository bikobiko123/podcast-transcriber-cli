from pathlib import Path

import pytest

from podcast_transcriber import resolver


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


def test_resolve_episode_fetches_xiaoyuzhou_page(monkeypatch) -> None:
    html = Path("tests/fixtures/xiaoyuzhou/episode_page.html").read_text(
        encoding="utf-8"
    )

    def fake_get(url: str, **kwargs) -> FakeResponse:
        assert url == "https://www.xiaoyuzhoufm.com/episode/65abc"
        assert kwargs["follow_redirects"] is True
        return FakeResponse(html)

    monkeypatch.setattr(resolver.httpx, "get", fake_get)

    episode = resolver.resolve_episode("https://www.xiaoyuzhoufm.com/episode/65abc")

    assert episode.title == "Demo Xiaoyuzhou Episode"
    assert episode.audio_url == "https://media.example.com/xiaoyuzhou-demo.m4a"


def test_resolve_episode_fetches_rss_feed(monkeypatch) -> None:
    xml = Path("tests/fixtures/rss/basic_feed.xml").read_text(encoding="utf-8")

    def fake_get(url: str, **kwargs) -> FakeResponse:
        assert url == "https://example.com/feed.xml"
        assert kwargs["follow_redirects"] is True
        return FakeResponse(xml)

    monkeypatch.setattr(resolver.httpx, "get", fake_get)

    episode = resolver.resolve_episode("https://example.com/feed.xml")

    assert episode.platform == "rss"
    assert episode.title == "Episode One"
    assert episode.audio_url == "https://media.example.com/episode-one.mp3"


def test_resolve_episode_identifies_apple_as_not_yet_supported() -> None:
    with pytest.raises(resolver.ResolverError, match="Apple Podcasts pages"):
        resolver.resolve_episode("https://podcasts.apple.com/us/podcast/demo/id123")
