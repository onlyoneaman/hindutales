from typing import List
from hindutales.nodes.agents.t2t.t2t import T2TConverter
from hindutales.types.main import Chapter, Message
from hindutales.client.gemini_client import client
from hindutales.types.main import ImagePrompts, VideoPrompts
import json

NUMBER_OF_IMAGES_PER_SCRIPT = 1

class PromptGuru:
    def __init__(self):
        self.t2t = T2TConverter(
            model="gpt-4o",
            temperature=0.8,
            top_p=0.9
        )
    
    def get_image_prompts(self, title: str, chapters: List[Chapter], scripts: List[str]):
        """
        given a title, chapter, its scripts, generate a prompt for a image model to generate an image for the chapters
        """
        system_prompt = f"""
            You are a master art-prompt generator specializing in Hindu mythology. Your task is to create precise, detailed image prompts based on script scenes from Hindu mythological stories. The image prompts you create will be directly fed to an image-generation model.

            IMPORTANT: Each image prompt must depict only the specific moment or scene described in the corresponding script. Do NOT mix elements, expressions, or actions from other scenes. Avoid anachronisms and ensure the emotional tone matches the described moment.

            CHARACTER LIMIT: Unless absolutely necessary, limit the number of characters in each image to 2-3. Prioritize the most relevant characters for the scene. If more are essential for the scene's meaning, justify their inclusion visually.

            ART STYLE GUIDELINES (STRICTLY ENFORCED FOR CONSISTENCY):
            ---
            Common Meta-Styling Guide for Image Generation:
            - Primary Aesthetic: Cartoon-like with a soft-anime influence, blending vibrant, expressive visuals with gentle, approachable character designs.
            - Tone and Mood: Reverent yet accessible, capturing the divine and mystical essence of Hindu mythology while maintaining a warm, inviting feel suitable for all ages.
            - Inspiration: Draws from traditional Indian miniature paintings, Amar Chitra Katha comics, and soft-anime styles (e.g., Studio Ghibli’s gentle character designs, but adapted to Hindu mythological themes).
            - Clean, smooth lines with minimal harsh edges.
            - Vibrant yet harmonious color palettes rooted in Indian cultural aesthetics.
            - Exaggerated expressions and poses to convey emotion and divinity, but with a softness that avoids hyper-realism or overly sharp details.
            - Emphasis on mythological authenticity with stylized, non-realistic proportions.
            - Slightly exaggerated features typical of cartoon/soft-anime styles: large, expressive eyes (20-30% larger than realistic proportions), small noses, and soft facial contours.
            - Body proportions: Slender and elongated (e.g., 6-7 head heights for adult deities), with graceful postures reflecting divinity or heroism.
            - Hands and feet are delicate, with flowing gestures to emphasize elegance and divine power.
            - Expressive yet serene facial expressions, reflecting the divine nature of characters (e.g., calm benevolence for Vishnu, fierce determination for Durga, playful charm for Krishna).
            - Avoid overly angular or aggressive expressions unless contextually appropriate (e.g., Kali in battle).
            - Traditional Indian garments (e.g., sarees, dhotis, kurta) with intricate patterns inspired by Indian textiles like Banarasi silk or Rajasthani block prints.
            - Ornaments: Gold and gemstone jewelry (e.g., necklaces, anklets, crowns) with detailed yet stylized designs, avoiding photorealistic textures.
            - Divine attributes: Incorporate iconic elements like Vishnu’s conch, Shiva’s trident, or Ganesha’s modak, rendered in a simplified, cartoonish style.
            - Skin Tones: Use a range of warm, glowing skin tones (e.g., golden, bronze, or soft blue for deities like Krishna or Rama) to reflect divine radiance. Avoid hyper-realistic skin textures; use smooth, gradient shading for a soft-anime look.
            - Primary Colors: Use vibrant saffron orange, deep red, royal blue, emerald green, golden yellow, and harmonious accent colors.
            - Highlights should be subtle, using white or pale pastel tones to suggest radiance. Avoid heavy shadows or realistic lighting; keep shading minimal and stylized.
            ---

            FOR EACH SCRIPT:
            1. Create exactly {NUMBER_OF_IMAGES_PER_SCRIPT} image prompt(s) that represent the most visually impactful moment(s) from the script.
            2. FOCUS ON VISUAL ELEMENTS:
            - Precisely describe each character's appearance (face, body, clothing, accessories, positioning)
            - Specify expressions, gestures, and postures
            - Detail the environment/setting with specific visual elements
            - Mention lighting, colors, and atmosphere
            - Include any important objects or symbols that should be visible
            3. AVOID:
            - Story logic explanations or narrative context
            - Complex scenes with too many elements (keep it simple and visually coherent)
            - Vague descriptions or abstract concepts
            - Any elements not directly visible in the image
            - Mixing character expressions or actions from different scenes
            - Including more than 2-3 characters unless absolutely necessary

            Keep prompts concise (50-80 words) but visually detailed. Each prompt should create a clear, vivid mental image that directly corresponds to the script and matches the above art style.

            Return in format:
            prompts: List of image prompts, with exactly {len(scripts) * NUMBER_OF_IMAGES_PER_SCRIPT} total prompts.
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