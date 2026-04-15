from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer

from podcast_transcriber.cleanup import cleanup_file
from podcast_transcriber.config import load_settings
from podcast_transcriber.downloader import download_audio
from podcast_transcriber.resolver import resolve_episode
from podcast_transcriber.summarizer import summarize
from podcast_transcriber.transcriber import FasterWhisperTranscriber, MlxWhisperTranscriber
from podcast_transcriber.writer import write_markdown


app = typer.Typer(help="Transcribe podcast links into Markdown files.")


@app.command()
def main(
    url: str,
    output_dir: Path | None = typer.Option(None, "--output-dir"),
    tmp_dir: Path | None = typer.Option(None, "--tmp-dir"),
    model: str | None = typer.Option(None, "--model"),
    backend: Literal["faster-whisper", "mlx"] = typer.Option(
        "faster-whisper",
        "--backend",
    ),
    beam_size: int = typer.Option(1, "--beam-size", min=1),
    language: str = typer.Option("auto", "--language"),
    summary: Literal["auto", "off", "agent", "api"] = typer.Option("auto", "--summary"),
) -> None:
    settings = load_settings()
    output_path = output_dir or Path(settings.transcript_dir)
    tmp_path = tmp_dir or Path(settings.tmp_dir)
    whisper_model = model or settings.whisper_model
    language_arg = None if language == "auto" else language

    _ensure_output_dir(output_path)

    typer.echo("Resolving episode...")
    episode = resolve_episode(url)
    typer.echo(f"Resolved: {episode.title}")

    audio_path: Path | None = None
    try:
        typer.echo("Downloading audio...")
        audio_path = download_audio(episode.audio_url, tmp_path)

        progress = _ProgressPrinter()
        if backend == "mlx":
            typer.echo(f"Transcribing with MLX Whisper model={whisper_model}...")
            mlx_transcriber = MlxWhisperTranscriber(model=whisper_model)
            transcript = mlx_transcriber.transcribe(
                audio_path,
                language=language_arg,
                progress_callback=progress,
            )
        else:
            typer.echo(f"Transcribing with Faster-Whisper model={whisper_model}...")
            transcriber = FasterWhisperTranscriber(
                model=whisper_model,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )
            transcript = transcriber.transcribe(
                audio_path,
                language=language_arg,
                beam_size=beam_size,
                progress_callback=progress,
            )

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


def _ensure_output_dir(output_path: Path) -> None:
    if output_path.exists():
        if not output_path.is_dir():
            raise typer.BadParameter(f"Output path is not a directory: {output_path}")
        return

    should_create = typer.confirm(
        f"Output directory does not exist: {output_path}. Create it?",
        default=False,
    )
    if not should_create:
        raise typer.Abort()
    output_path.mkdir(parents=True, exist_ok=True)


class _ProgressPrinter:
    def __init__(self) -> None:
        self._last_percent = -1

    def __call__(self, end_seconds: float, duration_seconds: float | None) -> None:
        if not duration_seconds:
            typer.echo(f"Transcribed through {end_seconds:.0f}s")
            return

        percent = min(100, int((end_seconds / duration_seconds) * 100))
        if percent >= self._last_percent + 5 or percent == 100:
            typer.echo(
                f"Transcription progress: {percent}% "
                f"({end_seconds:.0f}s/{duration_seconds:.0f}s)"
            )
            self._last_percent = percent
