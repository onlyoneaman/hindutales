from pydantic import BaseModel
from typing import List

class StoryOutput(BaseModel):
    story: str
    outline: List[str]
    title: str
    description: str

class ScriptsOutput(BaseModel):
    scripts: List[str]

class ImagePromptsOutput(BaseModel):
    image_prompts: List[str]

class ClipMeta(BaseModel):
    url: str
    duration: float
    file_path: str

class VideoMakerInput(BaseModel):
    prompt: str
    duration_seconds: float

class VideoMakerOutput(BaseModel):
    video_path: str
    used_clips: List[ClipMeta]
    script: str
    story: str
    srt: str
    keywords: List[str]


class VideoMakerResult(BaseModel):
    story: StoryOutput
    scripts: ScriptsOutput
    image_prompts: List[str]
    image_paths: List[str]
    audio_paths: List[str]
