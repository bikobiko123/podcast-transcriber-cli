from pathlib import Path
import struct
import wave
from types import SimpleNamespace

from podcast_transcriber.transcriber import (
    FasterWhisperTranscriber,
    MlxWhisperTranscriber,
    _load_audio_with_av,
    resolve_mlx_model,
)


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


def test_resolve_mlx_model_maps_common_names() -> None:
    assert resolve_mlx_model("small") == "mlx-community/whisper-small-mlx"
    assert resolve_mlx_model("large-v3") == "mlx-community/whisper-large-v3-mlx"
    assert resolve_mlx_model("mlx-community/custom") == "mlx-community/custom"


def test_mlx_transcriber_uses_mlx_api(tmp_path: Path) -> None:
    audio = tmp_path / "episode.mp3"
    audio.write_bytes(b"fake")
    calls: list[dict] = []

    def fake_transcribe(audio_data: object, **kwargs):
        calls.append({"audio_data": audio_data, **kwargs})
        return {
            "text": "hello from mlx",
            "language": "zh",
            "segments": [{"end": 2.5}],
        }

    progress: list[tuple[float, float | None]] = []
    transcriber = MlxWhisperTranscriber(
        model="small",
        transcribe_func=fake_transcribe,
        audio_loader=lambda path: f"loaded:{path.name}",
    )

    transcript = transcriber.transcribe(
        audio,
        language="zh",
        progress_callback=lambda end, duration: progress.append((end, duration)),
    )

    assert transcript.text == "hello from mlx"
    assert transcript.language == "zh"
    assert transcript.model == "mlx-community/whisper-small-mlx"
    assert transcript.backend == "mlx"
    assert calls == [
        {
            "audio_data": "loaded:episode.mp3",
            "path_or_hf_repo": "mlx-community/whisper-small-mlx",
            "language": "zh",
        }
    ]
    assert progress == [(2.5, None)]


def test_load_audio_with_av_returns_float_waveform(tmp_path: Path) -> None:
    audio = tmp_path / "tone.wav"
    samples = [0, 16384, -16384, 0]
    with wave.open(str(audio), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16_000)
        wav.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))

    waveform = _load_audio_with_av(audio)

    assert waveform.dtype.name == "float32"
    assert waveform.tolist() == [0.0, 0.5, -0.5, 0.0]
