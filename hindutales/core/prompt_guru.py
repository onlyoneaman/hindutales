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

Coomon ART STYLE GUIDELINES:
- Use a simple, vivid, and age-appropriate style.
- Use a color palette and style that is faithful to Hindu mythology but still modern.
- Create images in a cartoon-like, soft-anime style with clean, smooth lines and vibrant yet harmonious colors.
- Characters should have slightly exaggerated features: large expressive eyes, small noses, and soft facial contours.
- Use warm, glowing skin tones and slender, elongated proportions (6-7 head heights for adults).
- Depict traditional Indian garments (sarees, dhotis, kurtas) with simplified yet intricate patterns.
- Include proper divine attributes (e.g., Vishnu's conch, Shiva's trident, Ganesha's modak) in a stylized form.
- Use rich colors inspired by Indian festivals: saffron orange, deep red, royal blue, emerald green, and golden yellow.
- Add subtle halos or auras around deities using warm golds or cool blues to signify divinity.
- Create mystical backgrounds inspired by Hindu mythology (forests, celestial palaces, mountains).
- Employ soft gradient-based shading with minimal hard edges.
- Ensure culturally authentic and reverent depictions that maintain consistency across all images.
- Avoid photorealism, overly dark themes, or generic anime tropes that deviate from Hindu mythological aesthetics.

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
        