import pytest

from podcast_transcriber.config import Settings
from podcast_transcriber.summarizer import build_agent_summary_prompt, summarize


def test_build_agent_summary_prompt_contains_required_sections() -> None:
    prompt = build_agent_summary_prompt("hello transcript")
    assert "Core Points" in prompt
    assert "Supporting Arguments" in prompt
    assert "People, Companies, Concepts" in prompt
    assert "Actionable Takeaways" in prompt
    assert "Quote Candidates" in prompt
    assert "hello transcript" in prompt


def test_summary_api_mode_requires_key() -> None:
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        summarize("text", mode="api", settings=Settings(openai_api_key=None))
