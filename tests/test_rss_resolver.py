from pathlib import Path

from podcast_transcriber.resolvers.rss import parse_rss_items


def test_parse_rss_items_reads_enclosure() -> None:
    xml = Path("tests/fixtures/rss/basic_feed.xml").read_text(encoding="utf-8")
    episodes = parse_rss_items(xml, source_url="https://example.com/feed.xml")
    assert len(episodes) == 1
    assert episodes[0].title == "Episode One"
    assert episodes[0].audio_url == "https://media.example.com/episode-one.mp3"
    assert episodes[0].platform == "rss"
