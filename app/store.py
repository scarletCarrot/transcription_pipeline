from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from app.models import TranscriptJob


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, TranscriptJob] = {}
        self._lock = Lock()

    def add(self, job: TranscriptJob) -> TranscriptJob:
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> TranscriptJob | None:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **fields: object) -> TranscriptJob:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in fields.items():
                setattr(job, key, value)
            job.updated_at = datetime.now(timezone.utc).isoformat()
            return job


store = JobStore()
