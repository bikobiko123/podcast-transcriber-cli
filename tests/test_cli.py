from pathlib import Path

from typer.testing import CliRunner

from podcast_transcriber import cli
from podcast_transcriber.models import Episode, Transcript


def test_cli_pipeline_writes_markdown_and_cleans_audio(
    monkeypatch, tmp_path: Path
) -> None:
    audio = tmp_path / "tmp" / "episode.mp3"
    cleaned: list[Path] = []

    class FakeTranscriber:
        def __init__(self, model: str, device: str, compute_type: str) -> None:
            assert model == "small"
            assert device == "cpu"
            assert compute_type == "int8"

        def transcribe(
            self,
            audio_path: Path,
            language: str | None,
            beam_size: int,
            progress_callback,
        ) -> Transcript:
            assert audio_path == audio
            assert language is None
            assert beam_size == 1
            progress_callback(3.0, 3.0)
            return Transcript(
                text="hello transcript",
                language="en",
                duration_seconds=3.0,
                model="small",
            )

    monkeypatch.setattr(
        cli,
        "resolve_episode",
        lambda url: Episode(
            source_url=url,
            audio_url="https://media.example.com/episode.mp3",
            title="Demo Episode",
            platform="xiaoyuzhou",
        ),
    )
    monkeypatch.setattr(cli, "download_audio", lambda audio_url, tmp_dir: audio)
    monkeypatch.setattr(cli, "FasterWhisperTranscriber", FakeTranscriber)
    monkeypatch.setattr(
        cli,
        "summarize",
        lambda text, mode, settings: ("### Core Points\n\n- Fake summary.", "agent"),
    )
    monkeypatch.setattr(cli, "cleanup_file", lambda path: cleaned.append(path))

    result = CliRunner().invoke(
        cli.app,
        [
            "https://www.xiaoyuzhoufm.com/episode/demo",
            "--output-dir",
            str(tmp_path / "transcripts"),
            "--tmp-dir",
            str(tmp_path / "tmp"),
            "--summary",
            "agent",
        ],
    )

    assert result.exit_code == 0
    assert "Transcription progress: 100%" in result.stdout
    assert "Done:" in result.stdout
    output = tmp_path / "transcripts" / "demo-episode.md"
    assert output.exists()
    assert "hello transcript" in output.read_text(encoding="utf-8")
    assert cleaned == [audio]


def test_cli_can_select_mlx_backend(monkeypatch, tmp_path: Path) -> None:
    audio = tmp_path / "tmp" / "episode.mp3"
    cleaned: list[Path] = []

    class FakeMlxTranscriber:
        def __init__(self, model: str) -> None:
            assert model == "small"

        def transcribe(
            self,
            audio_path: Path,
            language: str | None,
            progress_callback,
        ) -> Transcript:
            assert audio_path == audio
            assert language == "zh"
            progress_callback(3.0, None)
            return Transcript(
                text="mlx transcript",
                language="zh",
                duration_seconds=None,
                model="mlx-community/whisper-small-mlx",
                backend="mlx",
            )

    monkeypatch.setattr(
        cli,
        "resolve_episode",
        lambda url: Episode(
            source_url=url,
            audio_url="https://media.example.com/episode.mp3",
            title="MLX Episode",
            platform="xiaoyuzhou",
        ),
    )
    monkeypatch.setattr(cli, "download_audio", lambda audio_url, tmp_dir: audio)
    monkeypatch.setattr(cli, "MlxWhisperTranscriber", FakeMlxTranscriber)
    monkeypatch.setattr(
        cli,
        "summarize",
        lambda text, mode, settings: ("### Core Points\n\n- Fake summary.", "agent"),
    )
    monkeypatch.setattr(cli, "cleanup_file", lambda path: cleaned.append(path))

    result = CliRunner().invoke(
        cli.app,
        [
            "https://www.xiaoyuzhoufm.com/episode/demo",
            "--backend",
            "mlx",
            "--language",
            "zh",
            "--output-dir",
            str(tmp_path / "transcripts"),
            "--tmp-dir",
            str(tmp_path / "tmp"),
            "--summary",
            "agent",
        ],
    )

    assert result.exit_code == 0
    assert "Transcribed through 3s" in result.stdout
    output = tmp_path / "transcripts" / "mlx-episode.md"
    assert output.exists()
    assert 'backend: "mlx"' in output.read_text(encoding="utf-8")
    assert cleaned == [audio]
