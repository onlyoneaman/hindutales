from pydantic import BaseModel
from typing import List
from io import BytesIO

class AudioMakerParams(BaseModel):
    paras: List[str]
    lang: str = "en"
    duration: int = 30

class VideoMakerParams(BaseModel):
    title: str
    lang: str = "en"
    duration: int = 30

class Chapter(BaseModel):
    title: str
    description: str

class PrimaryResult(BaseModel):
    title: str
    chapters: List[Chapter]

class Scripts(BaseModel):
    scripts: List[str]
    
class ImagePrompts(BaseModel):
    prompts: List[str]

class VideoPrompts(BaseModel):
    prompts: List[str]

class VideoMakerResult(BaseModel):
    title: str
    chapters: List[Chapter]
    scripts: List[str]
    image_prompts: ImagePrompts
    # video_prompts: VideoPrompts
    lang: str
    timestamp: str

class VideoGenInput(BaseModel):
    image_path: str
    video_prompt: str

class Message(BaseModel):
    role: str
    content: str
    
class AudioMakerResult:
    audios: list[BytesIO]