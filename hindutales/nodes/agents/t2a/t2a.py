import base64
from io import BytesIO
import json
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from dotenv import load_dotenv
from typing import List
from dataclasses import dataclass
from os import environ,getenv
import requests

load_dotenv()


@dataclass
class T2AOutput:
    audio: list[BytesIO]

class T2AConverter:
    def __init__(self, voice_id: str, model_id: str) -> None:
        self.voice_id = voice_id
        self.model_id = model_id
        apiKey=environ.get("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=apiKey)

    def generate(self, paragraphs: List[str], lang:str) -> T2AOutput:
        if lang.lower()!="english":
             return self.generate_using_sarvam(paragraphs=paragraphs,lang=lang)

        request_ids = []
        audio_buffers = []
        for paragraph in paragraphs:
            # Only pass the last 3 request_ids to comply with API constraints
            limited_request_ids = request_ids[-3:]
            with self.client.text_to_speech.with_raw_response.convert(
                text=paragraph,
                voice_id=self.voice_id,
                model_id=self.model_id,
                previous_request_ids=limited_request_ids
            ) as response:
                request_ids.append(response._response.headers.get("request-id"))
                audio_data = b''.join(chunk for chunk in response.data)
                audio_buffers.append(BytesIO(audio_data))

        return T2AOutput(audio=audio_buffers)
   
    def generate_using_sarvam(self, paragraphs: List[str], lang: str)->T2AOutput:
        api_subscription_key=getenv("SARVAM_API_KEY")
        url = "https://api.sarvam.ai/text-to-speech"
        headers = {
            "api-subscription-key": api_subscription_key,
            "Content-Type": "application/json"
        }

        target_language_code="mr-IN"
        if lang.lower()=="gujarati":
            target_language_code="gu-IN"
        if lang.lower()=="hindi":
            target_language_code="hi-IN"

        audio_buffers = []
        for paragraph in paragraphs:
            payload = {
                "text": paragraph,
                "target_language_code": target_language_code,
                "speaker":"karun",
                "model":"bulbul:v2",
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code >=200 and response.status_code<300:
                response_json = json.loads(response.content)
                audio_data_base64 = response_json["audios"][0]
                audio_data_bytes = base64.b64decode(audio_data_base64)
                audio_buffers.append(BytesIO(audio_data_bytes))
            else:
                raise Exception(f"Failed to generate speech from sarvam: {response.status_code}, {response.text}")  
        return T2AOutput(audio=audio_buffers)
