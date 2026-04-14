# Simple Transcription Pipeline

This project is a small, transcription service.
It accepts an audio upload, converts speech to text, stores the result, and formats the output for downstream use.

The goal was to keep the design practical and easy to explain, while still showing the main engineering decisions behind a real transcription pipeline.

## What the project does

- Accepts common audio formats like WAV, MP3, M4A, OGG, and FLAC
- Normalizes audio into a consistent WAV format with `ffmpeg`
- Transcribes audio with `faster-whisper` or a mock transcriber
- Returns transcript segments with timestamps
- Cleans and chunks transcript text for downstream use
- Handles multiple uploads by processing jobs in the background
- Retries failed transcription jobs up to 3 times
- Stores audio files separately from transcript JSON output

## Main API

### `POST /transcriptions`
Uploads an audio file and creates a transcription job.

### `GET /transcriptions/{job_id}`
Returns the current job status, transcript, timestamped segments, retry count, and any error.

### `GET /health`
Simple health check.

## Design decisions

### 1. Keep the request fast
I did not process transcription directly inside the upload request.
The API saves the file, creates a job, and submits it to a background worker.
That makes concurrent uploads easier to handle and avoids one long file blocking other requests.

In this version, the worker uses a `ThreadPoolExecutor`.
In a larger system, I would replace this with a real queue like Celery, Redis Queue, SQS, or Kafka-based workers.

### 2. Normalize audio formats first
Audio files can come in different formats.
Instead of making the transcription code deal with every format, I convert everything into a standard WAV file with:

- mono audio
- 16 kHz sample rate

This makes the transcription step more predictable and keeps the pipeline simpler.

### 3. Separate transcription from post-processing
The transcription layer only focuses on turning audio into text and segments.
Then a separate processor module handles:

- cleaning filler words like `um` and `uh`
- normalizing whitespace
- chunking text for downstream systems
- writing transcript JSON files

This separation makes the code easier to change later.
For example, I can replace the cleaning or chunking logic without touching the transcription code.

### 4. Include timestamps per segment
I returned segment-level timestamps instead of only one long transcript string.
That makes the result more useful for:

- subtitles
- search
- summarization
- highlighting exact moments in the audio
- future analytics

### 5. Store binary files separately from structured data
Audio files and transcript data have different storage needs.
So I kept them separate:

- audio files go under `data/audio/`
- transcript JSON files go under `data/transcripts/`

This project uses local storage for simplicity.
In production, I would likely use object storage like S3 for audio, and a database like Postgres for transcript metadata and job state.

### 6. Retry failed jobs
Transcription can fail for temporary reasons, like bad input, conversion issues, or model/runtime problems.
So each job has a status and retry count.
If a job fails, the system retries it up to 3 times.
If it still fails, it is marked as `failed` and the error is stored.

This helps recover from temporary failures without retrying forever.

### 7. Use a mock transcriber by default
For local testing and interview review, the project defaults to a mock transcriber.
That makes it easy to run without downloading the Whisper model.
If needed, it can switch to real transcription by setting:

```bash
export USE_MOCK_TRANSCRIBER=false
```

## Project structure

```text
transcription_pipeline/
├── app/
│   ├── main.py            # FastAPI app entry
│   ├── routes.py          # Upload and fetch endpoints
│   ├── queue_worker.py    # Background processing and retries
│   ├── transcriber.py     # Whisper and mock transcription
│   ├── audio_utils.py     # File validation and format conversion
│   ├── processor.py       # Cleanup, chunking, transcript output
│   ├── storage.py         # Audio/transcript file storage
│   ├── store.py           # In-memory job state store
│   └── models.py          # Job and segment models
├── tests/
│   └── test_processor.py
├── requirements.txt
└── README.md
```

## End-to-end flow

1. Client uploads an audio file to `POST /transcriptions`
2. API validates the extension
3. Audio file is saved under `data/audio/`
4. A transcription job is added to the in-memory store
5. A background worker picks up the job
6. Audio is converted to normalized WAV with `ffmpeg`
7. The transcriber creates text + timestamped segments
8. The processor cleans and chunks the transcript
9. A transcript JSON file is written to `data/transcripts/`
10. Client checks the result with `GET /transcriptions/{job_id}`

## Running the project

### Requirements

- Python 3.10+
- `ffmpeg` installed and available in PATH

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run with mock transcriber

```bash
export USE_MOCK_TRANSCRIBER=true
uvicorn app.main:app --reload
```

### Run with Whisper

```bash
export USE_MOCK_TRANSCRIBER=false
uvicorn app.main:app --reload
```

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/transcriptions" \
  -H "accept: application/json" \
  -F "file=@sample.mp3"
```

## Example response

```json
{
  "job_id": "abc123",
  "status": "pending",
  "message": "Upload accepted. Transcription started."
}
```

## Tradeoffs and what I would improve next

This project is intentionally simple.
It is meant to show the thinking, not to act like a full production system.

If I extended it further, I would add:

- real queue infrastructure instead of an in-process executor
- Postgres or Redis for persistent job tracking
- object storage like S3 for uploaded audio
- authentication and rate limiting
- better logging and metrics
- support for long-audio chunking before transcription
- optional speaker diarization
- async notification when a job is complete

## Summary

The main idea behind this solution was:

- keep the upload API simple
- move processing to the background
- normalize audio early
- separate audio storage from transcript storage
- return timestamps for downstream usefulness
- make failures recoverable with retries

That gives a small but clean codebase that is easy to explain in an interview and easy to grow later.
