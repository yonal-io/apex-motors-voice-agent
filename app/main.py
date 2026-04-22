# app/main.py
# FastAPI entry point. Serves the Twilio voice webhook and static audio files.
# On startup: pre-generates the greeting MP3 via ElevenLabs if not already cached.

# Standard library imports
from pathlib import Path
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from twilio.twiml.voice_response import VoiceResponse

# Local application imports
from app import config
from app.speech.tts import synthesize


# Constants
STATIC_DIR = Path("static")
GREETING_PATH = STATIC_DIR / "greeting.mp3"
GREETING_TEXT = "Hi, thanks for calling Apex Motors! This is Sam — how can I help you today?"

# Create static dir at module level (before app is created)
# so StaticFiles mount doesn't error on missing directory.
STATIC_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not GREETING_PATH.exists():
        audio_bytes = synthesize(GREETING_TEXT)
        with open(GREETING_PATH, "wb") as f:
            f.write(audio_bytes)
    print("Startup complete: Greeting audio checked and ready.")
    yield

# Wires startup/shutdown function to the app lifecycle
app = FastAPI(lifespan=lifespan)
# Serve static/ directory at /static/ so Twilio can fetch audio files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Health check endpoint to verify the server is running
@app.get("/")
def health_check():
    return{"status":"ok"}

# Twilio voice webhook endpoint. Twilio will POST here when a call comes in.
@app.post("/voice")
def voice_webhook():
    response = VoiceResponse()
    response.play(f"{config.APP_URL}/static/greeting.mp3")
    response.hangup() # End the call after playing the greeting
    twiml = str(response)
    return Response(content=twiml, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
