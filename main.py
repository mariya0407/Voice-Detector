from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import base64
import os
import uuid
import time
from brain import analyze_audio
from pathlib import Path

app = FastAPI(
    title="Veritas AI API",
    description="Use the Authorize button to set the x-api-key header for requests.",
)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
VALID_API_KEY = os.getenv("VOICE_API_KEY", "sk_test_123456789")
TEMP_FOLDER = BASE_DIR / "temp_audio"
TEMP_FOLDER.mkdir(parents=True, exist_ok=True)
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ALLOWED_LANGUAGES = {
    "tamil": "Tamil",
    "english": "English",
    "hindi": "Hindi",
    "malayalam": "Malayalam",
    "telugu": "Telugu",
}

# Data Model
class VoiceRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str

# Security Check
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return api_key

@app.get("/")
async def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")

@app.post("/api/voice-detection")
async def detect_voice(request: VoiceRequest, api_key: str = Depends(verify_api_key)):
    # 1. Start timer (for the 'Efficiency' metric)
    start_time = time.time()

    if request.audioFormat.lower() != "mp3":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format. Only MP3 is supported.")

    language_key = request.language.strip().lower()
    if language_key not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language. Supported: Tamil, English, Hindi, Malayalam, Telugu.",
        )
    normalized_language = ALLOWED_LANGUAGES[language_key]

    # 2. Decode Audio
    try:
        base64_data = request.audioBase64
        if "base64," in base64_data:
            base64_data = base64_data.split("base64,", 1)[1]
        audio_bytes = base64.b64decode(base64_data)
        file_id = str(uuid.uuid4())
        file_path = TEMP_FOLDER / f"{file_id}.mp3"
        
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed Base64 data")

    # 3. Analyze
    try:
        classification, confidence, explanation = analyze_audio(str(file_path))
    finally:
        # 4. Cleanup: Always delete the file, even if analysis fails
        if file_path.exists():
            file_path.unlink()

    # 5. Measure speed
    _ = round(time.time() - start_time, 3)

    return {
        "status": "success",
        "language": normalized_language,
        "classification": classification,
        "confidenceScore": confidence,
        "explanation": explanation
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"status": "error", "message": "Invalid request body"},
    )
