from hindutales.nodes.agents.t2a.t2a import T2AConverter
from io import BytesIO
from hindutales.types.main import AudioMakerParams

class AudioMaker:
    def __init__(self, params: AudioMakerParams) -> None:
        self.paras: list[str] = params.paras
        self.lang: str = params.lang
        self.duration: int = params.duration
        self.t2a = T2AConverter(
            model_id="eleven_flash_v2_5",
            voice_id="yco9hkSzXpAeaJXfPNpa",
        )

    def generate(self) -> list[BytesIO]:
        audios = self.t2a.generate(self.paras)
        return audios.audio