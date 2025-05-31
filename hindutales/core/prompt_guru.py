from typing import List
from hindutales.nodes.agents.t2t.t2t import T2TConverter
from hindutales.types.main import Chapter, Message
from hindutales.client.gemini_client import client
from hindutales.types.main import ImagePrompts, VideoPrompts
import json

class PromptGuru:
    def __init__(self):
        self.t2t = T2TConverter(
            model="gpt-4o",
            temperature=0.8,
            top_p=0.9
        )
    
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
        messages: List[Message] = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=f"Story title: {title}", chapters=[chapter.model_dump() for chapter in chapters], scripts=scripts),
        ]
        resp = self.t2t.generate(
            input_data=messages,
            system_prompt=system_prompt,
            user_prompt=f"Story title: {title}",
            output_type=ImagePrompts
        )
        try:
            return resp
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}")
        
    def get_video_prompts(self, title: str, chapters: List[Chapter], scripts: List[str]):
        """
        given a title, chapter, its scripts, generate a prompt for a video model to generate a video for the chapters
        """
        system_prompt = """
        We are writing a Hindu mythology story. The story consists of many scenes.
We want to generate a video for each scene.

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

Return a list of prompts for the video equal to the number of chapters.
Use best video prompting techniques to generate the video.

Return in format:
prompts: List of prompts for the video.
        """
        user_msg = f"Story title: {title}, chapters: {chapters}, scripts: {scripts}"
        resp = self.t2t.generate(
            system_prompt=system_prompt,
            user_prompt=user_msg,
            output_type=VideoPrompts
        )
        try:
            return resp
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}")