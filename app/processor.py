from __future__ import annotations

import json
import re
from pathlib import Path

from app.models import Segment
from app.storage import TRANSCRIPT_DIR


class TranscriptProcessor:
    def clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\b(um+|uh+|erm)\b", "", text, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", text).strip()

    def chunk_text(self, text: str, chunk_size: int = 300) -> list[str]:
        if len(text) <= chunk_size:
            return [text] if text else []
        chunks: list[str] = []
        current = ""
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = sentence
        if current:
            chunks.append(current)
        return chunks

    def save_result(self, job_id: str, transcript: str, segments: list[Segment]) -> str:
        cleaned = self.clean_text(transcript)
        payload = {
            "job_id": job_id,
            "transcript": transcript,
            "cleaned_transcript": cleaned,
            "chunks": self.chunk_text(cleaned),
            "segments": [seg.__dict__ for seg in segments],
        }
        output = TRANSCRIPT_DIR / f"{job_id}.json"
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(output)
