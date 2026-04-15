from pathlib import Path
from types import SimpleNamespace

from podcast_transcriber.transcriber import FasterWhisperTranscriber


class FakeModel:
    def __init__(self) -> None:
        self.kwargs = {}

    def transcribe(self, audio_path: str, language: str | None, **kwargs):
        self.kwargs = kwargs
        segments = (
            segment
            for segment in [
                SimpleNamespace(start=0.0, end=1.0, text=" hello"),
                SimpleNamespace(start=1.0, end=2.0, text=" world"),
            ]
        )
        info = SimpleNamespace(language="en", duration=2.0)
        return segments, info


def test_transcriber_collects_generator_text(tmp_path: Path) -> None:
    audio = tmp_path / "episode.mp3"
    audio.write_bytes(b"fake")
    model = FakeModel()
    transcriber = FasterWhisperTranscriber(
        model="small",
        model_factory=lambda *_, **__: model,
    )
    progress: list[tuple[float, float | None]] = []

    transcript = transcriber.transcribe(
        audio,
        language=None,
        progress_callback=lambda end, duration: progress.append((end, duration)),
    )

    assert transcript.text == "hello world"
    assert transcript.language == "en"
    assert transcript.duration_seconds == 2.0
    assert transcript.model == "small"
    assert model.kwargs["vad_filter"] is True
    assert model.kwargs["beam_size"] == 1
    assert model.kwargs["best_of"] == 1
    assert model.kwargs["temperature"] == 0.0
    assert model.kwargs["condition_on_previous_text"] is False
    assert progress == [(1.0, 2.0), (2.0, 2.0)]
