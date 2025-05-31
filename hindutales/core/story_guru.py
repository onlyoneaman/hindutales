from hindutales.client.gemini_client import client
from hindutales.types.main import PrimaryResult, Scripts
import json

class StoryGuru:
    def __init__(self):
        pass

    def generate_outline(self, title: str, lang: str):
        system_prompt = (
            "You are a creative short-form video writer expert. Your goal is to create a 30s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. "
            "Given a prompt, generate: "
            "1. A title for the video."
            "2. Outline of the video in chapters. Each chapter should be atleast 15 seconds long. Keep chapter title short"
            "Return a JSON with keys: title, chapters."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Theme: {title}"},
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
            return PrimaryResult(
                title=parsed.get("title", ""),
                chapters=parsed.get("chapters", []),
            )
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}\nRaw output: {getattr(resp.choices[0].message, 'content', '')}")

    def generate_scripts(self, primary_result: PrimaryResult) -> Scripts:
        system_prompt = (
            "You are a creative short-form video writer expert. Your goal is to create a 30s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. "
            "Given a prompt, generate: "
            "Scripts for the video in chapters. Each chapter should be atleast 15 seconds long. Keep chapter title short"
            "Return a JSON with keys: scripts."
        )
        chapters_data = [chapter.model_dump() for chapter in primary_result.chapters]
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Theme: {primary_result.title}", "chapters": chapters_data},
        ]
        resp = client.beta.chat.completions.parse(
            model="gemini-2.0-flash-lite",
            messages=messages,
            temperature=0.8,
            top_p=0.9,
            response_format=Scripts
        )
        try:
            content = resp.choices[0].message.content
            if isinstance(content, dict):
                parsed = content
            else:
                parsed = json.loads(content)
            return Scripts(
                scripts=parsed.get("scripts", []),
            )
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}\nRaw output: {getattr(resp.choices[0].message, 'content', '')}")