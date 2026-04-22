# Wraps the ElevenLabs SDK to convert text into audio bytes.
# Used by main.py at startup to generate greeting.mp3
# and to generate per-response audio over WebSocket.

from elevenlabs.client import ElevenLabs
from app import config

# Create one ElevenLabs client instance at module level
client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

# Converts text to speech using ElevenLabs and returns the full audio as bytes.
def synthesize(text: str) -> bytes:
    audio_iterator = client.text_to_speech.convert(
        voice_id=config.ELEVENLABS_VOICE_ID,
        text = text,
        model_id="eleven_turbo_v2_5",
        output_format="mp3_44100_64"
    )
    # Concatenate the byte chunks into a single bytes object
    audio_data = b"".join(audio_iterator)
    return audio_data
