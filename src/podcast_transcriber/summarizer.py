from __future__ import annotations

from openai import OpenAI

from podcast_transcriber.config import Settings


SUMMARY_TEMPLATE = """### Core Points

### Supporting Arguments

### People, Companies, Concepts

### Actionable Takeaways

### Quote Candidates
"""


def build_agent_summary_prompt(transcript: str) -> str:
    return f"""Use the transcript below to fill this structured podcast summary in Markdown.

Return only the completed summary sections.

{SUMMARY_TEMPLATE}

Transcript:

{transcript}
"""


def summarize(transcript: str, mode: str, settings: Settings) -> tuple[str, str]:
    if mode == "off":
        return "", "off"

    if mode == "agent" or (mode == "auto" and not settings.openai_api_key):
        return (
            f"{SUMMARY_TEMPLATE}\n\n## Summary Prompt\n\n{build_agent_summary_prompt(transcript)}",
            "agent",
        )

    if mode == "api" and not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required when --summary api is used")

    if mode == "auto" and settings.openai_api_key:
        return _summarize_with_api(transcript, settings), "api"

    if mode == "api":
        return _summarize_with_api(transcript, settings), "api"

    raise ValueError(f"Unsupported summary mode: {mode}")


def _summarize_with_api(transcript: str, settings: Settings) -> str:
    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You create concise structured Markdown summaries of podcast "
                    "transcripts."
                ),
            },
            {
                "role": "user",
                "content": build_agent_summary_prompt(transcript),
            },
        ],
    )
    content = response.choices[0].message.content
    return content or SUMMARY_TEMPLATE
