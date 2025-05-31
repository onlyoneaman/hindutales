from dataclasses import dataclass
from pydantic import BaseModel
from typing import List
import json
from hindutales.client.gemini_client import client

@dataclass(frozen=True)
class VideoMakerParams:
    title: str
    lang: str = "en"
    duration: int = 30

@dataclass(frozen=True)
class VideoMakerResult:
    title: str
    chapters: List[str]
    lang: str

class Chapter(BaseModel):
    title: str
    description: str

class PrimaryResult(BaseModel):
    title: str
    chapters: List[Chapter]

class VideoMaker:
    def __init__(self, params: VideoMakerParams) -> None:
        self.title: str = params.title
        self.lang: str = params.lang
        self.duration: int = params.duration

    def generate(self) -> VideoMakerResult:
        # Placeholder: Add GeminiClient integration here
        # Generate chapters and a processed title
        primary_result = self.generate_primary_result()
        return VideoMakerResult(
            title=primary_result.title,
            chapters=primary_result.chapters,
            lang=self.lang
        )

    def generate_primary_result(self) -> PrimaryResult:
        # Placeholder: Add GeminiClient integration here
        # Generate chapters and a processed title
        system_prompt = (
            "You are a creative short-form video writer expert. Your goal is to create a 30s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. "
            "Given a prompt, generate: "
            "1. A title for the video."
            "2. Outline of the video in chapters. Each chapter should be atleast 15 seconds long. Keep chapter title short"
            "Return a JSON with keys: title, chapters."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Theme: {self.title}"},
        ]
        resp = client.beta.chat.completions.parse(
            model="gemini-2.0-flash-lite",
            messages=messages,
            temperature=0.8,
            top_p=0.9,
            response_format=PrimaryResult
        )
        try:
            content = resp.choices[0].message.content
            if isinstance(content, dict):
                parsed = content
            else:
                parsed = json.loads(content)
            title = parsed.get("title", "")
            chapters = parsed.get("chapters", [])
            # If chapters is a string, split
            if isinstance(chapters, str):
                chapters = [k.strip() for k in chapters.split(",") if k.strip()]
            return PrimaryResult(
                title=title,
                chapters=chapters,
            )
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}\nRaw output: {getattr(resp.choices[0].message, 'content', '')}")
