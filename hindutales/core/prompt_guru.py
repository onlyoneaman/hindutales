from typing import List
from hindutales.types.main import Chapter
from hindutales.client.gemini_client import client
from hindutales.types.main import ImagePrompts
import json

class PromptGuru:
    def __init__(self):
        pass
    
    def get_image_prmopts(self, title: str, chapters: List[Chapter], scripts: List[str]):
        """
        given a title, chapter, its scripts, generate a prompt for a image model to generate an image for the chapters
        """
        system_prompt = """
        We are writing a Hindu mythology story. The story consists of many scenes.
We want to generate an image for each scene.
Guidelines:
- Use a simple, vivid, and age-appropriate style.
- Use a color palette and style that is faithful to Hindu mythology but still modern.

We will provide the story title, description, current scene title and story, and previous and next scene titles if available.

Return a list of prompts for the image equal to the number of chapters.
Use best image prompting techniques to generate the image.

Return in format:
prompts: List of prompts for the image.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Story title: {title}", "chapters": [chapter.model_dump() for chapter in chapters], "scripts": scripts},
        ]
        resp = client.beta.chat.completions.parse(
            model="gemini-2.0-flash-lite",
            messages=messages,
            temperature=0.8,
            top_p=0.9,
            response_format=ImagePrompts
        )
        try:
            content = resp.choices[0].message.content
            if isinstance(content, dict):
                parsed = content
            else:
                parsed = json.loads(content)
            return ImagePrompts(
                prompts=parsed.get("prompts", []),
            )
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}\nRaw output: {getattr(resp.choices[0].message, 'content', '')}")
        