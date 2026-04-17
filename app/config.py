import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY      = os.environ["OPENAI_API_KEY"]
TWILIO_ACCOUNT_SID  = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN   = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
DEEPGRAM_API_KEY    = os.environ["DEEPGRAM_API_KEY"]
ELEVENLABS_API_KEY  = os.environ["ELEVENLABS_API_KEY"]
ELEVENLABS_VOICE_ID = os.environ["ELEVENLABS_VOICE_ID"]
RESEND_API_KEY      = os.environ["RESEND_API_KEY"]
EMAIL_RECIPIENT     = os.environ["EMAIL_RECIPIENT"]
EMAIL_FROM          = os.environ["EMAIL_FROM"]
APP_URL             = os.environ["APP_URL"]
