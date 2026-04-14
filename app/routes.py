from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.audio_utils import validate_extension
from app.models import TranscriptJob
from app.queue_worker import submit_job
from app.storage import save_audio_file
from app.store import store

router = APIRouter()


@router.post("/transcriptions")
def create_transcription(file: UploadFile = File(...)) -> dict:
    try:
        validate_extension(file.filename or "")
        audio_path, storage_key = save_audio_file(file.filename or "audio.bin", file.file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = TranscriptJob(filename=file.filename or "audio.bin", audio_path=audio_path, storage_key=storage_key)
    store.add(job)
    submit_job(job.id)
    return {
        "job_id": job.id,
        "status": job.status,
        "message": "Upload accepted. Transcription started.",
    }


@router.get("/transcriptions/{job_id}")
def get_transcription(job_id: str) -> dict:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "retries": job.retries,
        "error": job.error,
        "transcript": job.transcript,
        "segments": [seg.__dict__ for seg in job.segments],
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
