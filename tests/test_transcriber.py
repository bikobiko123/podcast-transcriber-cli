from pathlib import Path
from types import SimpleNamespace

from podcast_transcriber.transcriber import FasterWhisperTranscriber


class FakeModel:
    def transcribe(self, audio_path: str, language: str | None, vad_filter: bool):
        segments = [
            SimpleNamespace(start=0.0, end=1.0, text=" hello"),
            SimpleNamespace(start=1.0, end=2.0, text=" world"),
        ]
        info = SimpleNamespace(language="en", duration=2.0)
        return segments, info


def test_transcriber_collects_generator_text(tmp_path: Path) -> None:
    audio = tmp_path / "episode.mp3"
    audio.write_bytes(b"fake")
    transcriber = FasterWhisperTranscriber(
        model="small",
        model_factory=lambda *_, **__: FakeModel(),
    )

    transcript = transcriber.transcribe(audio, language=None)

    assert transcript.text == "hello world"
    assert transcript.language == "en"
    assert transcript.duration_seconds == 2.0
    assert transcript.model == "small"
