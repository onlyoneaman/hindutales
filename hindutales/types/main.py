from pydantic import BaseModel
from typing import List

class VideoMakerParams(BaseModel):
    title: str
    lang: str = "en"
    duration: int = 30

class Chapter(BaseModel):
    title: str
    description: str

class VideoMakerResult(BaseModel):
    title: str
    chapters: List[Chapter]
    lang: str

class PrimaryResult(BaseModel):
    title: str
    chapters: List[Chapter]