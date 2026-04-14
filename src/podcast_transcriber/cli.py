from __future__ import annotations

import typer

from podcast_transcriber.config import load_settings


app = typer.Typer(help="Transcribe podcast links into Markdown files.")


@app.command()
def main(url: str) -> None:
    settings = load_settings()
    typer.echo(f"podcast-transcribe is installed. URL={url}")
    typer.echo(f"default model={settings.whisper_model}")
