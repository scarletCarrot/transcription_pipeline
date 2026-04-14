from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.audio_utils import convert_to_wav
from app.processor import TranscriptProcessor
from app.store import store
from app.transcriber import MockTranscriber, WhisperTranscriber

MAX_RETRIES = 3
executor = ThreadPoolExecutor(max_workers=4)
processor = TranscriptProcessor()
USE_MOCK = os.getenv("USE_MOCK_TRANSCRIBER", "true").lower() == "true"
transcriber = MockTranscriber() if USE_MOCK else WhisperTranscriber()


def submit_job(job_id: str) -> None:
    executor.submit(process_job, job_id)


def process_job(job_id: str) -> None:
    job = store.get(job_id)
    if job is None:
        return

    store.update(job_id, status="processing", error=None)
    wav_path = None
    try:
        wav_path = convert_to_wav(job.audio_path)
        transcript, segments = transcriber.transcribe(wav_path)
        output_path = processor.save_result(job_id, transcript, segments)
        store.update(
            job_id,
            status="completed",
            transcript=transcript,
            segments=segments,
            error=None,
        )
    except Exception as exc:
        retries = job.retries + 1
        if retries < MAX_RETRIES:
            store.update(job_id, status="pending", retries=retries, error=str(exc))
            submit_job(job_id)
        else:
            store.update(job_id, status="failed", retries=retries, error=str(exc))
    finally:
        if wav_path and Path(wav_path).exists():
            Path(wav_path).unlink(missing_ok=True)
