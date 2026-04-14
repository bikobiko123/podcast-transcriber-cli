from podcast_transcriber.downloader import audio_filename_from_url


def test_audio_filename_from_url_keeps_extension() -> None:
    assert (
        audio_filename_from_url("https://cdn.example.com/path/My Show.m4a?token=1")
        == "my-show.m4a"
    )
