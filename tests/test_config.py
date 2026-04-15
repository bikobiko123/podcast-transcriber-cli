from podcast_transcriber.config import Settings


def test_default_settings_are_local_first() -> None:
    settings = Settings()
    assert settings.whisper_model == "small"
    assert settings.whisper_device == "cpu"
    assert settings.whisper_compute_type == "int8"
    assert (
        settings.transcript_dir
        == "/Users/bikodemac/Desktop/code-workspace/biko 仓库-真/00_收件箱"
    )
    assert settings.tmp_dir == "tmp"
