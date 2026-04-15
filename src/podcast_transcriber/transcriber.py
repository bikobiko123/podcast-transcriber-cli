from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel

from podcast_transcriber.models import Transcript

ProgressCallback = Callable[[float, float | None], None]
MlxTranscribeFunc = Callable[..., dict[str, Any]]
AudioLoader = Callable[[Path], Any]

MLX_MODEL_ALIASES = {
    "tiny": "mlx-community/whisper-tiny-mlx",
    "base": "mlx-community/whisper-base-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
    "turbo": "mlx-community/whisper-large-v3-turbo",
}


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
            backend="faster-whisper",
        )


class MlxWhisperTranscriber:
    def __init__(
        self,
        model: str = "small",
        transcribe_func: MlxTranscribeFunc | None = None,
        audio_loader: AudioLoader | None = None,
    ) -> None:
        self.model_name = resolve_mlx_model(model)
        self._transcribe_func = transcribe_func or _load_mlx_transcribe()
        self._audio_loader = audio_loader or _load_audio_with_av

    def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> Transcript:
        kwargs: dict[str, Any] = {"path_or_hf_repo": self.model_name}
        if language is not None:
            kwargs["language"] = language

        audio_data = self._audio_loader(audio_path)
        result = self._transcribe_func(audio_data, **kwargs)
        segments = result.get("segments") or []
        end_seconds = _last_segment_end(segments)
        if progress_callback is not None:
            progress_callback(end_seconds, None)

        return Transcript(
            text=str(result.get("text") or "").strip(),
            language=str(result.get("language") or language or "unknown"),
            duration_seconds=end_seconds or None,
            model=self.model_name,
            backend="mlx",
        )


def resolve_mlx_model(model: str) -> str:
    return MLX_MODEL_ALIASES.get(model, model)


def _load_mlx_transcribe() -> MlxTranscribeFunc:
    try:
        import mlx_whisper
    except ImportError as exc:
        raise RuntimeError(
            "MLX backend requires optional dependencies. Install them with: "
            'python -m pip install -e ".[mlx]"'
        ) from exc
    return mlx_whisper.transcribe


def _load_audio_with_av(audio_path: Path, sample_rate: int = 16_000) -> Any:
    import av
    import numpy as np

    chunks = []
    with av.open(str(audio_path)) as container:
        stream = next(
            (candidate for candidate in container.streams if candidate.type == "audio"),
            None,
        )
        if stream is None:
            return np.array([], dtype=np.float32)

        resampler = av.audio.resampler.AudioResampler(
            format="s16",
            layout="mono",
            rate=sample_rate,
        )
        for frame in container.decode(stream):
            resampled_frames = resampler.resample(frame)
            if not isinstance(resampled_frames, list):
                resampled_frames = [resampled_frames]
            for resampled in resampled_frames:
                array = resampled.to_ndarray()
                chunks.append(array.reshape(-1))

    if not chunks:
        return np.array([], dtype=np.float32)

    return np.concatenate(chunks).astype(np.float32) / 32768.0


def _last_segment_end(segments: object) -> float:
    end_seconds = 0.0
    if not isinstance(segments, list):
        return end_seconds
    for segment in segments:
        if isinstance(segment, dict):
            end_seconds = max(end_seconds, float(segment.get("end") or 0.0))
    return end_seconds
