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


def test_parse_episode_page_extracts_json_ld_audio() -> None:
    html = """
    <html>
      <head>
        <meta property="og:title" content="JSON LD Episode" />
        <script type="application/ld+json">
          {
            "@context": "https://schema.org",
            "@type": "PodcastEpisode",
            "associatedMedia": {
              "@type": "MediaObject",
              "contentUrl": "https://media.example.com/json-ld.m4a"
            }
          }
        </script>
      </head>
      <body></body>
    </html>
    """

    episode = parse_episode_page(
        html,
        source_url="https://www.xiaoyuzhoufm.com/episode/jsonld",
    )

    assert episode.title == "JSON LD Episode"
    assert episode.audio_url == "https://media.example.com/json-ld.m4a"


def test_parse_episode_page_extracts_next_data_enclosure_audio() -> None:
    html = """
    <html>
      <head>
        <meta property="og:title" content="Next Data Episode" />
        <script id="__NEXT_DATA__" type="application/json">
          {
            "props": {
              "pageProps": {
                "episode": {
                  "enclosure": {
                    "url": "https://media.example.com/next-data.m4a"
                  }
                }
              }
            }
          }
        </script>
      </head>
      <body></body>
    </html>
    """

    episode = parse_episode_page(
        html,
        source_url="https://www.xiaoyuzhoufm.com/episode/nextdata",
    )

    assert episode.title == "Next Data Episode"
    assert episode.audio_url == "https://media.example.com/next-data.m4a"
