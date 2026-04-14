from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path("data")
AUDIO_DIR = BASE_DIR / "audio"
TRANSCRIPT_DIR = BASE_DIR / "transcripts"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)


def save_audio_file(filename: str, file_obj) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower() or ".bin"
    key = f"{uuid4()}{suffix}"
    destination = AUDIO_DIR / key
    with destination.open("wb") as out:
        shutil.copyfileobj(file_obj, out)
    return str(destination), key
