from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel

from podcast_transcriber.models import Transcript

ProgressCallback = Callable[[float, float | None], None]


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

    def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
        beam_size: int = 1,
        progress_callback: ProgressCallback | None = None,
    ) -> Transcript:
        segments, info = self._model.transcribe(
            str(audio_path),
            language=language,
            vad_filter=True,
            beam_size=beam_size,
            best_of=1,
            temperature=0.0,
            condition_on_previous_text=False,
        )
        duration = getattr(info, "duration", None)
        parts: list[str] = []
        for segment in segments:
            segment_text = segment.text.strip()
            if segment_text:
                parts.append(segment_text)
            if progress_callback is not None:
                progress_callback(float(getattr(segment, "end", 0.0)), duration)
        return Transcript(
            text=" ".join(parts),
            language=getattr(info, "language", language or "unknown"),
            duration_seconds=duration,
            model=self.model_name,
        )
