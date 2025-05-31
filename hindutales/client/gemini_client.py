import os
# from google import genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it to your Google API key.")

# Gemini google genai client
# gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)