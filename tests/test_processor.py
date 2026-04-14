from app.processor import TranscriptProcessor


def test_clean_text_removes_fillers() -> None:
    processor = TranscriptProcessor()
    result = processor.clean_text("um hello   uh there")
    assert result == "hello there"
