from podcast_transcriber.downloader import audio_filename_from_url
from podcast_transcriber.downloader import download_audio


def test_audio_filename_from_url_keeps_extension() -> None:
    assert (
        audio_filename_from_url("https://cdn.example.com/path/My Show.m4a?token=1")
        == "my-show.m4a"
    )


def test_download_audio_reuses_existing_non_empty_file(monkeypatch, tmp_path) -> None:
    existing = tmp_path / "show.m4a"
    existing.write_bytes(b"already downloaded")

    def fail_stream(*args, **kwargs):
        raise AssertionError("download should not be called")

    monkeypatch.setattr("podcast_transcriber.downloader.httpx.stream", fail_stream)

    path = download_audio("https://cdn.example.com/show.m4a", tmp_path)

    assert path == existing
    assert path.read_bytes() == b"already downloaded"
