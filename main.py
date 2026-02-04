from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import base64
import os
import uuid
import time
from brain import analyze_audio

app = FastAPI(title="Veritas AI API")

# Configuration
VALID_API_KEY = "sk_test_123456789"
TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Data Model
class VoiceRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str

# Security Check
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.get("/")
async def serve_frontend():
    return FileResponse('static/index.html')

@app.post("/api/voice-detection")
async def detect_voice(request: VoiceRequest, api_key: str = Depends(verify_api_key)):
    # 1. Start timer (for the 'Efficiency' metric)
    start_time = time.time()

    if request.audioFormat.lower() != "mp3":
        raise HTTPException(status_code=400, detail="Invalid format. Only MP3 is supported.")

    # 2. Decode Audio
    try:
        audio_bytes = base64.b64decode(request.audioBase64)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(TEMP_FOLDER, f"{file_id}.mp3")
        
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
    except Exception:
        return {"status": "error", "message": "Malformed Base64 data"}

    # 3. Analyze
    try:
        classification, confidence, explanation = analyze_audio(file_path)
    finally:
        # 4. Cleanup: Always delete the file, even if analysis fails
        if os.path.exists(file_path):
            os.remove(file_path)

    # 5. Measure speed
    process_time = round(time.time() - start_time, 3)

    return {
        "status": "success",
        "language": request.language,
        "classification": classification,
        "confidenceScore": confidence,
        "explanation": explanation,
        "processingTime": f"{process_time}s"
    }