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
        system_prompt = (
            f"You are a master art-prompt generator specializing in Hindu mythology. Your task is to create precise, detailed image prompts based on script scenes from Hindu mythological stories. The image prompts you create will be directly fed to an image-generation model."

            f"CHRONOLOGICAL ACCURACY (CRITICAL):"
            f"- Process scripts in strict chronological order"
            f"- Each prompt must ONLY depict the specific moment from its corresponding script"
            f"- First prompt MUST represent the opening scene/moment of the story"
            f"- Never mix or reference elements from future scenes"

            f"EMOTIONAL EXPRESSION GUIDELINES:" 
            f"- Match expressions EXACTLY to the emotional state described in the current scene"
            f"- Use subtle, balanced expressions unless the scene explicitly calls for intensity"
            f"- When emotional context is ambiguous, default to neutral or slightly positive expressions"
            f"- Avoid extreme emotions unless specifically mentioned in the script"

            f"CHARACTER LIMIT: Unless absolutely necessary, limit the number of characters in each image to 2-3. Prioritize the most relevant characters for the scene. If more are essential for the scene's meaning, justify their inclusion visually."

            f"ART STYLE GUIDELINES (STRICTLY ENFORCED FOR CONSISTENCY):"
            f"---"
            f"Common Meta-Styling Guide for Image Generation:"
            f"- Primary Aesthetic: Cartoon-like with a soft-anime influence, blending vibrant, expressive visuals with gentle, approachable character designs."
            f"- Tone and Mood: Reverent yet accessible, capturing the divine and mystical essence of Hindu mythology while maintaining a warm, inviting feel suitable for all ages."
            f"- Inspiration: Draws from traditional Indian miniature paintings, Amar Chitra Katha comics, and soft-anime styles (e.g., Studio Ghibli's gentle character designs, but adapted to Hindu mythological themes)."
            f"- Clean, smooth lines with minimal harsh edges."
            f"- Vibrant yet harmonious color palettes rooted in Indian cultural aesthetics."
            f"- Exaggerated expressions and poses to convey emotion and divinity, but with a softness that avoids hyper-realism or overly sharp details."
            f"- Emphasis on mythological authenticity with stylized, non-realistic proportions."
            f"- Exaggerated expressions and poses to convey emotion and divinity, but with a softness that avoids hyper-realism or overly sharp details."
            f"- Emphasis on mythological authenticity with stylized, non-realistic proportions."
            f"- Slightly exaggerated features typical of cartoon/soft-anime styles: large, expressive eyes (20-30% larger than realistic proportions), small noses, and soft facial contours."
            f"- Body proportions: Slender and elongated (e.g., 6-7 head heights for adult deities), with graceful postures reflecting divinity or heroism."
            f"- Hands and feet are delicate, with flowing gestures to emphasize elegance and divine power."
            f"- Expressive yet serene facial expressions, reflecting the divine nature of characters (e.g., calm benevolence for Vishnu, fierce determination for Durga, playful charm for Krishna)."
            f"- Avoid overly angular or aggressive expressions unless contextually appropriate (e.g., Kali in battle)."
            f"- Traditional Indian garments (e.g., sarees, dhotis, kurta) with intricate patterns inspired by Indian textiles like Banarasi silk or Rajasthani block prints."
            f"- Ornaments: Gold and gemstone jewelry (e.g., necklaces, anklets, crowns) with detailed yet stylized designs, avoiding photorealistic textures."
            f"- Divine attributes: Incorporate iconic elements like Vishnu's conch, Shiva's trident, or Ganesha's modak, rendered in a simplified, cartoonish style."
            f"- Skin Tones: Use a range of warm, glowing skin tones (e.g., golden, bronze, or soft blue for deities like Krishna or Rama) to reflect divine radiance. Avoid hyper-realistic skin textures; use smooth, gradient shading for a soft-anime look."
            f"- Primary Colors: Use vibrant saffron orange, deep red, royal blue, emerald green, golden yellow, and harmonious accent colors."
            f"- Highlights should be subtle, using white or pale pastel tones to suggest radiance. Avoid heavy shadows or realistic lighting; keep shading minimal and stylized."
            f"---"

            f"FOR EACH SCRIPT:"
            f"1. For a given script, create {NUMBER_OF_IMAGES_PER_SCRIPT} image prompts that represent the most visually impactful moment(s) from the script."
            f"2. FOCUS ON VISUAL ELEMENTS:"
            f"- Precisely describe each character's appearance (face, body, clothing, accessories, positioning)"
            f"- Specify expressions, gestures, and postures"
            f"- Detail the environment/setting with specific visual elements"
            f"- Mention lighting, colors, and atmosphere"
            f"- Include any important objects or symbols that should be visible"
            f"- Mention lighting, colors, and atmosphere"
            f"- Include any important objects or symbols that should be visible"
            f"- Mention lighting, colors, and atmosphere"
            f"- Include any important objects or symbols that should be visible"
            f"3. AVOID:"
            f"- Story logic explanations or narrative context"
            f"- Complex scenes with too many elements (keep it simple and visually coherent)"
            f"- Vague descriptions or abstract concepts"
            f"- Any elements not directly visible in the image"
            f"- Mixing character expressions or actions from different scenes"
            f"- Including more than 2-3 characters unless absolutely necessary"

            f"Keep prompts concise (50-100 words) but visually detailed. Each prompt should create a clear, vivid mental image that directly corresponds to the script and matches the above art style."

            f"Return in format:"
            f"prompts: List of image prompts, with exactly {len(scripts) * NUMBER_OF_IMAGES_PER_SCRIPT} total prompts."
        )
        resp = self.t2t.generate(
            system_prompt=system_prompt,
            user_prompt=f"Story title: {title} content= Story title: {title}, chapters={[chapter.model_dump() for chapter in chapters]}, scripts={scripts}",
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