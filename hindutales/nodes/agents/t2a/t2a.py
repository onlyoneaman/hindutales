from io import BytesIO
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from dotenv import load_dotenv
from typing import List
from dataclasses import dataclass
from os import environ

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

    def generate(self, paragraphs: List[str]) -> T2AOutput:
        request_ids = []
        audio_buffers = []
        for paragraph in paragraphs:
            # Usually we get back a stream from the convert function, but with_raw_response is
            # used to get the headers from the response
            with self.client.text_to_speech.with_raw_response.convert(
                text=paragraph,
                voice_id=self.voice_id,
                model_id=self.model_id,
                previous_request_ids=request_ids
            ) as response:
                request_ids.append(response._response.headers.get("request-id"))
                # response._response.headers also contains useful information like 'character-cost',
                # which shows the cost of the generation in characters.
                audio_data = b''.join(chunk for chunk in response.data)
                audio_buffers.append(BytesIO(audio_data))

        return T2AOutput(audio=audio_buffers)
    
