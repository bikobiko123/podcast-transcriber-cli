from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel

from podcast_transcriber.models import Transcript


class FasterWhisperTranscriber:
    def __init__(
        self,
        model: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        model_factory: Callable[..., Any] = WhisperModel,
    ) -> None:
        self.model_name = model
        self._model = model_factory(model, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: Path, language: str | None = None) -> Transcript:
        segments, info = self._model.transcribe(
            str(audio_path),
            language=language,
            vad_filter=True,
        )
        text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
        return Transcript(
            text=text,
            language=getattr(info, "language", language or "unknown"),
            duration_seconds=getattr(info, "duration", None),
            model=self.model_name,
        )
