from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

JobStatus = Literal["pending", "processing", "completed", "failed"]


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptJob:
    filename: str
    audio_path: str
    storage_key: str
    status: JobStatus = "pending"
    transcript: str | None = None
    segments: list[Segment] = field(default_factory=list)
    retries: int = 0
    error: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
