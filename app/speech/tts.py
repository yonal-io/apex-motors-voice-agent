# Wraps the ElevenLabs SDK to convert text into audio bytes.
# Single public function: synthesize(text) -> bytes
# Used by main.py at startup to generate greeting.mp3,
# and later (Step 3+) to generate per-response audio over WebSocket.

# --- imports ---
# import the ElevenLabs client class from the elevenlabs SDK
from elevenlabs.client import ElevenLabs
# import config so we can access ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID
from app import config

# --- client setup ---
# create one ElevenLabs client instance at module level
# (created once when the module is first imported, reused on every call)
client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

# --- synthesize function ---
# converts text to speech using ElevenLabs and returns the full audio as bytes.
def synthesize(text: str) -> bytes:
    audio_iterator = client.text_to_speech.convert( # Call the TTS conversion method
        voice_id=config.ELEVENLABS_VOICE_ID, # Pass the voice ID from config
        text = text, # Pass the input text to be synthesized
        model_id="eleven_turbo_v2_5", # Specify the high-speed model
        output_format="mp3_44100_64" # Set audio format to 44.1kHz 64kbps MP3
    )
    # The SDK returns an iterator of byte chunks, NOT a single bytes object
    # Concatenate the generator chunks into a single bytes object
    audio_data = b"".join(audio_iterator)
    return audio_data

