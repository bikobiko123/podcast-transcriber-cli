from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer

from podcast_transcriber.cleanup import cleanup_file
from podcast_transcriber.config import load_settings
from podcast_transcriber.downloader import download_audio
from podcast_transcriber.resolver import resolve_episode
from podcast_transcriber.summarizer import summarize
from podcast_transcriber.transcriber import FasterWhisperTranscriber
from podcast_transcriber.writer import write_markdown


app = typer.Typer(help="Transcribe podcast links into Markdown files.")


@app.command()
def main(
    url: str,
    output_dir: Path | None = typer.Option(None, "--output-dir"),
    tmp_dir: Path | None = typer.Option(None, "--tmp-dir"),
    model: str | None = typer.Option(None, "--model"),
    language: str = typer.Option("auto", "--language"),
    summary: Literal["auto", "off", "agent", "api"] = typer.Option("auto", "--summary"),
) -> None:
    settings = load_settings()
    output_path = output_dir or Path(settings.transcript_dir)
    tmp_path = tmp_dir or Path(settings.tmp_dir)
    whisper_model = model or settings.whisper_model
    language_arg = None if language == "auto" else language

    typer.echo("Resolving episode...")
    episode = resolve_episode(url)
    typer.echo(f"Resolved: {episode.title}")

    audio_path: Path | None = None
    try:
        typer.echo("Downloading audio...")
        audio_path = download_audio(episode.audio_url, tmp_path)

        typer.echo(f"Transcribing with Faster-Whisper model={whisper_model}...")
        transcriber = FasterWhisperTranscriber(
            model=whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        transcript = transcriber.transcribe(audio_path, language=language_arg)

        typer.echo("Preparing summary...")
        summary_markdown, summary_mode = summarize(
            transcript.text,
            mode=summary,
            settings=settings,
        )

        markdown_path = write_markdown(
            episode=episode,
            transcript=transcript,
            output_dir=output_path,
            summary_markdown=summary_markdown,
            summary_mode=summary_mode,
        )
        typer.echo(f"Done: {markdown_path}")
    finally:
        if audio_path is not None:
            cleanup_file(audio_path)
