import concurrent.futures
from io import BytesIO
from elevenlabs import ForcedAlignmentResponseModel, VoiceSettings

from hindutales.constants.models import LatestModels
from hindutales.clients.ai_img_client import AIImgClient
from hindutales.clients.elevenlabs_client import elevenlabs_client
from hindutales.models.video import StoryOutput, ScriptsOutput, ImagePromptsOutput
from hindutales.utils.llm_utils import get_llm_response

PER_CHAPTER_DURATION = 12
WORDS_PER_MINUTE = 170
IMAGES_PER_CHAPTER = 1

def get_story_outline(prompt: str, description: str, duration_seconds: int, lang: str) -> StoryOutput:
    """Uses Gemini client to get story, outline, title, and description from a prompt."""

    num_chapters = duration_seconds // PER_CHAPTER_DURATION

    system_prompt = f"""
        You are a creative short-form video writer expert. Your goal is to create a {duration_seconds}s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. 
        Given a theme / prompt and a description, generate:
        story to set the flow on how the video should be structured, using a good initial hook, going into story, dramatic climax, and resolution if any.
        outline for the video, dividing the story into {num_chapters} parts. We will use this outline to create subtitles for each part as well as graphics for scenes.
        each outline would roughly cover {PER_CHAPTER_DURATION}s of the video.
        title for the video. outlines should only be a excerpt of this part of the story.
        description for the video. keep it short and informative. dont include any hashtags. 
        Overall this video should be factually correct and educational.       
        Focus on correctness, coherence, depth, and clarity.
        It would be great if we can draw some inspiration from this story as well.
        Do NOT invent or alter events, characters, or facts unless explicitly asked for a fictionalized version.
        Generate the story, outline, title, and description in {lang}.

        Return a JSON with keys: story (str), outline (list of str), title (str), description (str).
    """
    user_prompt = (
        "Theme: {prompt}"
        "Description: {description}"
        "Number of chapters: {num_chapters}"
        "Language: {lang}"
    ).format(prompt=prompt, description=description, num_chapters=num_chapters, lang=lang)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    resp = get_llm_response(
        messages=messages,
        response_format=StoryOutput,
        model=LatestModels.gemini_high,
        allow_fallback=True
    )
    return resp


def create_scripts(output: StoryOutput, duration_seconds: int, lang: str) -> ScriptsOutput:
    """
    Uses Gemini to generate scripts for a story.
    """
    title = output.title
    story = output.story
    outline = output.outline
    old_system_prompt = (
        f"You are an expert storyteller and a creative short-form video writer. Your goal is to create engaging scripts for chapters of a story, "
        f"with each script corresponding to a specific chapter from the provided info. Most importantly, the scripts must be factually accurate."
        f"Do NOT invent or alter events, characters, or facts unless explicitly asked for a fictionalized version."
        f"We are creating a overall {duration_seconds}s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. "
        "Given a title, brief story and an outline that together form a complete story, generate scripts for each outline or part of the story. "
        "Dont include any hashtags in the scripts, or any very difficult words. "
        "Generate scripts for each part of the story, total number of scripts should be equal to the number of outline parts. "
        f"Each script would be around {PER_CHAPTER_DURATION}s long."
        "Provide a list of scripts that when combined form a coherent and continuous narrative that tells the complete story."
        "It would be great if we can draw some inspiration from this story as well."
        "Return a JSON with keys: scripts (list of strings)."
    )
    # this system prompt creates a single script for the story
    system_prompt = (
        f"You are an expert storyteller and a creative short-form video writer. Your goal is to create engaging script for a story, "
        f"Most importantly, the scripts must be factually accurate."
        f"Do NOT invent or alter events, characters, or facts unless explicitly asked for a fictionalized version."
        f"We are creating a overall {duration_seconds}s YouTube Short or Instagram Reel that is engaging, entertaining, and educational. "
        "Given a title, brief story and an outline that together form a complete story, generate script for the story. "
        "Dont include any hashtags in the scripts, or any very difficult words. "
        "Provide a script that forms a coherent and continuous narrative that tells the complete story."
        "Add a hook at the start of the script to make it engaging and interesting if possible"
        f"The script should be around {duration_seconds}s long and we would follow {WORDS_PER_MINUTE} words per minute. Keep this in mind while writing the script."
        "Reflect back on script to make sure it follows given duration and words per minute."
        "Examples for hooks: "
        "1. What If i told you?"
        "2. Have you ever wondered"
        "3. Ever wondered why"
        "4. Have you heard the story of"
        "It would be great if we can draw some inspiration from this story as well."
        f"Generate the script in {lang}."
        "Return a JSON with keys: scripts (list of strings) with only 1 string."
    )
    user_prompt = (
        "Title: {title}"
        "Story: {story}"
        "Chapters: {outline}"
        "Number of scripts: {num_scripts}"
        "Language: {lang}"
    ).format(title=title, story=story, outline=outline, num_scripts=len(outline), lang=lang)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    resp = get_llm_response(
        messages=messages,
        model=LatestModels.gemini_mid,
        response_format=ScriptsOutput,
        allow_fallback=True
    )
    return resp
    

# create new method which takes storyOutput, subtitles and creates image prompts for each part
def create_image_prompts(story: StoryOutput, scripts: ScriptsOutput, duration_seconds: int) -> ImagePromptsOutput:
    """
    Uses Gemini to generate image prompts for a story.
    """
    story_text = story.story
    outlines = story.outline
    num_chapters = len(outlines)
    scripts = scripts.scripts
    system_prompt = (
        "You are a creative visual storyteller specializing in emotionally resonant, painterly imagery for short-form videos like YouTube Shorts and Instagram Reels."
        "Your goal is to generate vivid, cinematic image prompts for each part of a story. "
        f"Each image prompt should be around {IMAGES_PER_CHAPTER} images per chapter."
        f"Total number of image prompts should be equal to the {IMAGES_PER_CHAPTER * num_chapters}."

        "VISUAL TONE & STYLE GUIDELINES (STRICTLY ENFORCED):\n\n"

        "Primary Aesthetic:\n"
        "- Textured, emotional, hand-painted style reminiscent of Raja Ravi Varma and 19th-century Indian portraiture.\n"
        "- Emphasize visible brushstrokes, canvas texture, soft chiaroscuro lighting, and rich shadow depth.\n"
        "- Prioritize emotional realism, warmth, and imperfection over digital polish or cartoonish exaggeration.\n\n"

        "Mood and Emotion:\n"
        "- Focus on facial expression and posture that reflect the emotion in the script—soft sorrow, dignified anger, divine serenity, etc.\n"
        "- Avoid extremes unless specified. Use naturalistic, painterly emotion—expressive but grounded.\n\n"

        "Color and Light:"
        "- Use muted, earthy tones, soft golds, maroons, deep blues, and candlelit warmth for divine or intimate scenes.\n"
        "- Avoid neon colors, digital gradients, or highly saturated comic-style palettes.\n"
        "- Lighting should evoke mood—dim, diffused, temple glows, twilight riversides, oil lamp shimmer.\n\n"

        "Style and Costume:"
        "- Characters wear traditional Indian garments—sarees, dhotis, angavastrams—based on the historical/mythological era.\n"
        "- Jewelry and ornaments should be detailed but not photorealistic: filigreed gold, rudraksha beads, antique nose rings.\n"
        "- Hair should reflect realism—wet strands, braided locks, unkempt during emotional scenes.\n\n"

        "Scene Composition:\n"
        "- Focus on 1–2 characters when possible. More only if required for context.\n"
        "- Highlight emotion through close-ups, side profiles, and cinematic framing.\n"
        "- Environment should reflect physical space: temple interiors, riverside banks, royal courts, warfields—described with natural elements (mist, shadows, flickering lamps).\n\n"

        "Negative Styling (by exclusion):\n"
        "- Avoid cartoon, anime, 3D rendering, photorealistic CGI, over-polished digital art\n"
        "- Avoid flat backgrounds, smooth gradients, unrealistic symmetry, or plastic-like faces\n\n"

        "Final Guidelines:"
        "- Do not include text or story narration—only describe what's visually present."
        "- Focus each prompt on one meaningful moment."
        "- Each prompt should be 100–300 words and detailed enough to create a vivid painterly image from scratch using language from guidelines shared above."
        "- We will use this image prompts to create graphics for scenes, the creator understands above guidelines so try to include as much detail as possible for better quality graphics."
        "- Return a JSON with key: image_prompts (list of strings)."
    )
    user_prompt = f"Story: {story_text}\nOutline: {outlines}\nScripts: {scripts}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    resp = get_llm_response(
        messages=messages,
        model=LatestModels.gemini_high,
        response_format=ImagePromptsOutput
    )
    return resp


def create_images(image_prompts: list[str]) -> list[bytes]:
    ai_img_client = AIImgClient()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks and store them with their original index
        future_to_index = {
            executor.submit(ai_img_client.generate_image_from_text, prompt): i 
            for i, prompt in enumerate(image_prompts)
        }
        
        # Initialize results list with None placeholders
        images = [None] * len(image_prompts)
        
        # Collect results and place them in the correct order
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            image_bytes = future.result()
            images[index] = image_bytes
    
    return images


def create_audios(scripts: list[str], language: str = "english") -> list[BytesIO]:
    request_ids = []
    audio_buffers = []
    model_id = "eleven_flash_v2_5"
    # voice_id = "yco9hkSzXpAeaJXfPNpa"
    voice_id = "Pj6TyxlNO6XhJZGbTEHO"
    for idx, script in enumerate(scripts):
        limited_request_ids = request_ids[-3:]
        script = scripts[idx]
        next_text = scripts[idx + 1] if idx + 1 < len(scripts) else ""
        with elevenlabs_client.text_to_speech.with_raw_response.convert(
            text=script,
            model_id=model_id,
            voice_id=voice_id,
            previous_request_ids=limited_request_ids,
            next_text=next_text,
            voice_settings=VoiceSettings(
                speed=1.15,
            )
        ) as response:
            request_id = response._response.headers.get("request-id")
            audio_data = b''.join(chunk for chunk in response.data)
            audio_buffers.append(BytesIO(audio_data))
            request_ids.append(request_id)
    return audio_buffers

def get_forced_alignment(audio_path: str, scripts: list[str]) -> ForcedAlignmentResponseModel:
    full_text = "\n".join(scripts)
    try:
        audio_file_bytes = open(audio_path, "rb").read()
        resp = elevenlabs_client.forced_alignment.create(
            file=audio_file_bytes,
            text=full_text,
        )
        return resp
    except Exception as e:
        raise ValueError(f"Failed to get forced alignment: {e}")
