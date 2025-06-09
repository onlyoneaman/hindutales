from hindutales.nodes.agents.t2a.t2a import T2AConverter
from io import BytesIO
from hindutales.types.main import AudioMakerParams
from hindutales.client.elevenlabs_client import elevenlabs_client

class AudioMaker:
    def __init__(self, params: AudioMakerParams) -> None:
        self.paras: list[str] = params.paras
        self.lang: str = params.lang
        self.duration: int = params.duration
        self.elevenlabs_client = elevenlabs_client
        self.elevenlabs_voice_id = "yco9hkSzXpAeaJXfPNpa"
        self.elevenlabs_model_id = "eleven_flash_v2_5"
        self.t2a = T2AConverter(
            model_id=self.elevenlabs_model_id,
            voice_id=self.elevenlabs_voice_id,
        )

    def generate(self) -> list[BytesIO]:
        audios = self.t2a.generate(paragraphs=self.paras,lang=self.lang)
        return audios.audio

    def create_audio(self):
        with self.elevenlabs_client.text_to_speech.with_raw_response.convert(
            text=self.paras,
            voice_id=self.elevenlabs_voice_id,
            model_id=self.elevenlabs_model_id,
            previous_request_ids=[]
        ) as response:
            audio_data = b''.join(chunk for chunk in response.data)
            audio_buffer = BytesIO(audio_data)
            return audio_buffer
    
    def forceed_alignment(self):
        aligns = self.elevenlabs_client.forced_alignment.convert(
            text=self.paras,
            voice_id=self.elevenlabs_voice_id,
            model_id=self.elevenlabs_model_id,
            previous_request_ids=[]
        )
        return aligns