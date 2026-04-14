# Simple Transcription Pipeline

A small interview-ready project that:
- accepts WAV/MP3 style uploads
- normalizes audio with ffmpeg
- transcribes with Whisper (or mock mode by default)
- stores audio separately from transcript data
- processes jobs in the background to handle concurrent uploads
- retries failed jobs up to 3 times
- returns transcript segments with timestamps

## API

### Upload audio
`POST /transcriptions`

### Check result
`GET /transcriptions/{job_id}`

## Run

### Windows (PowerShell)

From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:USE_MOCK_TRANSCRIBER = "true"
uvicorn app.main:app --reload
```

If `Activate.ps1` is blocked, in PowerShell run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` (CurrentUser scope does not require an elevated shell), or use **Command Prompt** below.

### Windows (Command Prompt)

```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
set USE_MOCK_TRANSCRIBER=true
uvicorn app.main:app --reload
```

### macOS / Linux (bash)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export USE_MOCK_TRANSCRIBER=true
uvicorn app.main:app --reload
```

Set `USE_MOCK_TRANSCRIBER=false` to use `faster-whisper` instead: PowerShell `$env:USE_MOCK_TRANSCRIBER = "false"`; Command Prompt `set USE_MOCK_TRANSCRIBER=false`; bash `export USE_MOCK_TRANSCRIBER=false`.

Install **ffmpeg** and ensure it is on your `PATH` (on Windows, `ffmpeg -version` in a new terminal should work).

## Notes

- Audio files are stored under `data/audio/`
- Processed transcript JSON files are stored under `data/transcripts/`
- In a real production version, I would swap the in-memory store for Postgres/Redis and use S3 for file storage.
