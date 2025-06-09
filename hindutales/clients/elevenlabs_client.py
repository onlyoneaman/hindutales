from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable is not set. Please set it to your ElevenLabs API key.")

elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)