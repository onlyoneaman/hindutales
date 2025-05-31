from typing import List
from hindutales.nodes.agents.t2t.t2t import T2TConverter
from hindutales.types.main import PrimaryResult, Scripts, Message

class StoryGuru:
    def __init__(self):
        pass
        self.t2t = T2TConverter(
            model="gpt-4o",
            temperature=0.8,
            top_p=0.9
        )

    def generate_outline(self, title: str, lang: str):
        system_prompt = (
            "You are a creative short-form video writer expert. Your goal is to create a 30s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. "
            "Given a prompt, generate: "
            "1. A title for the video."
            "2. Outline of the video in chapters. Each chapter should be atleast 15 seconds long. Keep chapter title short"
            "Return a JSON with keys: title, chapters."
        )
        messages: List[Message] = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=f"Theme: {title}")
        ]
        resp = self.t2t.generate(
            input_data=messages,
            system_prompt=system_prompt,
            user_prompt=f"Theme: {title}",
            output_type=PrimaryResult
        )
        try:
            return resp
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}")

    def generate_scripts(self, primary_result: PrimaryResult) -> Scripts:
        system_prompt = (
            "You are a creative short-form video writer expert. Your goal is to create a 30s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. "
            "Given a prompt, generate: "
            "Scripts for the video in chapters. Each chapter should be atleast 15 seconds long. Keep chapter title short"
            "Return a JSON with keys: scripts."
        )
        chapters_data = [chapter.model_dump() for chapter in primary_result.chapters]
        messages: List[Message] = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=f"Theme: {primary_result.title}", chapters=chapters_data),
        ]
        resp = self.t2t.generate(
            input_data=messages,
            system_prompt=system_prompt,
            user_prompt=f"Theme: {primary_result.title}",
            output_type=Scripts
        )
        try:
            return resp
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}")