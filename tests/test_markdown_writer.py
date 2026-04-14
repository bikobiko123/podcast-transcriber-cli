from pathlib import Path

from podcast_transcriber.models import Episode, Transcript
from podcast_transcriber.writer import safe_slug, write_markdown


def test_safe_slug_keeps_chinese_and_ascii_words() -> None:
    assert safe_slug("EP. 12: AI 产品 | 小宇宙?") == "ep-12-ai-产品-小宇宙"


def test_write_markdown_creates_one_episode_file(tmp_path: Path) -> None:
    episode = Episode(
        source_url="https://www.xiaoyuzhoufm.com/episode/demo",
        audio_url="https://media.example.com/demo.mp3",
        title="Demo Episode",
        platform="xiaoyuzhou",
        description="A useful episode.",
    )
    transcript = Transcript(
        text="hello world",
        language="en",
        duration_seconds=12.5,
        model="small",
    )

    output = write_markdown(
        episode=episode,
        transcript=transcript,
        output_dir=tmp_path,
        summary_markdown="### Core Points\n\n- One useful point.",
        summary_mode="agent",
    )

    assert output.name.endswith("demo-episode.md")
    content = output.read_text(encoding="utf-8")
    assert 'title: "Demo Episode"' in content
    assert 'platform: "xiaoyuzhou"' in content
    assert "## Summary" in content
    assert "## Transcript" in content
    assert "hello world" in content
