from __future__ import annotations

from typing import Any

try:
    from faster_whisper import WhisperModel
except Exception:  # pragma: no cover
    WhisperModel = None  # type: ignore

from app.models import Segment


class Transcriber:
    def transcribe(self, wav_path: str) -> tuple[str, list[Segment]]:
        raise NotImplementedError


class WhisperTranscriber(Transcriber):
    def __init__(self, model_name: str = "base", device: str = "cpu") -> None:
        if WhisperModel is None:
            raise RuntimeError("faster-whisper is not installed")
        self.model = WhisperModel(model_name, device=device)

    def transcribe(self, wav_path: str) -> tuple[str, list[Segment]]:
        segments, _ = self.model.transcribe(wav_path)
        parsed = [
            Segment(start=round(seg.start, 2), end=round(seg.end, 2), text=seg.text.strip())
            for seg in segments
        ]
        transcript = " ".join(seg.text for seg in parsed).strip()
        return transcript, parsed


class MockTranscriber(Transcriber):
    def transcribe(self, wav_path: str) -> tuple[str, list[Segment]]:
        segments = [
            Segment(start=0.0, end=2.1, text="Hello and welcome to the demo."),
            Segment(start=2.1, end=4.8, text="This is mock transcription output."),
        ]
        transcript = " ".join(seg.text for seg in segments)
        return transcript, segments
