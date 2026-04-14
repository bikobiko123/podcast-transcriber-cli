from pathlib import Path

from podcast_transcriber.cleanup import cleanup_file


def test_cleanup_file_removes_existing_file(tmp_path: Path) -> None:
    audio = tmp_path / "episode.mp3"
    audio.write_bytes(b"audio")
    cleanup_file(audio)
    assert not audio.exists()


def test_cleanup_file_ignores_missing_file(tmp_path: Path) -> None:
    cleanup_file(tmp_path / "missing.mp3")
