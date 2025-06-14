from typing import List
from hindutales.nodes.agents.t2t.t2t import T2TConverter
from hindutales.types.main import PrimaryResult, Scripts, Message

# story -> chapters -> scripts, videos
LENGTH_OF_STORY_IN_SECONDS = 60
NUMBER_OF_CHAPTERS_PER_STORY = 5
NUMBER_OF_SCRIPTS_PER_CHAPTER = 1
NUMBER_OF_VIDEOS_PER_CHAPTER = 1
LENGTH_OF_SCRIPT_IN_SECONDS = LENGTH_OF_STORY_IN_SECONDS / (NUMBER_OF_CHAPTERS_PER_STORY * NUMBER_OF_SCRIPTS_PER_CHAPTER)


class StoryGuru:
    def __init__(self):
        self.t2t = T2TConverter()

    def generate_outline(self, title: str, description: str):
        """
        Goals:
        1. break down story in such parts where the total story can be of length 1-1.5 minutes
        2. the stories should be factually correct and cohenerent with indian mythology.
        """
        system_prompt = (
            f"You are an expert mythological storyteller and a creative short-form video writer. Your primary goal is to create a {LENGTH_OF_STORY_IN_SECONDS} seconds long YouTube Short or Instagram Reel that is engaging, educational, and, most importantly, factually accurate to authentic Indian mythology.\n"
            f"You must focus on correctness, coherence, and depth, drawing only from real mythological sources, scriptures, and epics (such as the Ramayana, Mahabharata, Puranas, Vedas, etc.). Do NOT invent or alter events, characters, or facts unless explicitly asked for a fictionalized version."
            f"Given a prompt return JSON with"
            f"1. A title for the video that will be the story's title."
            f"2. A description for the video that will be the story's description."
            f"3. An outline of the video in chapters. Chapters must be divided such that, conceptually, describing each chapter in both audio and video format should take roughly equal time. Keep chapter titles short, but ensure each chapter is a logical and authentic segment of the mythological narrative."
            f"4. There should be exactly {NUMBER_OF_CHAPTERS_PER_STORY} chapters for the given story."
            f"Return a JSON with keys: title, description, chapters."
        )
        messages: List[Message] = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=f"Theme: {title}, description: {description}")
        ]

        resp = self.t2t.generate(
            input_data=messages,
            system_prompt=system_prompt,
            user_prompt=f"Theme: {title}, description: {description}",
            output_type=PrimaryResult
        )
        try:
            return resp
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}")

    def generate_scripts(self, primary_result: PrimaryResult, lang: str) -> Scripts:
        system_prompt = (
            f"You are an expert mythological storyteller and a creative short-form video writer. Your goal is to create scripts for chapters of a story, with each script corresponding to a specific chapter from the provided primary result. Most importantly, the scripts must be factually accurate to authentic Indian mythology.\n\n"
            f"You must focus on correctness, coherence, and depth, drawing only from real mythological sources, scriptures, and epics (such as the Ramayana, Mahabharata, Puranas, Vedas, etc.). Do NOT invent or alter events, characters, or facts unless explicitly asked for a fictionalized version.\n\n"
            f"You will be given a list of chapters that together form a complete story. For each chapter, you will generate {NUMBER_OF_SCRIPTS_PER_CHAPTER} scripts that describe that specific chapter in detail. When combined, all scripts should form a coherent and continuous narrative that tells the complete story.\n"
            f"The scripts should be in {lang}.\n"
            f"Requirements:\n"
            f"1. Generate EXACTLY {NUMBER_OF_CHAPTERS_PER_STORY * NUMBER_OF_SCRIPTS_PER_CHAPTER} total scripts ({NUMBER_OF_SCRIPTS_PER_CHAPTER} scripts per chapter for {NUMBER_OF_CHAPTERS_PER_STORY} chapters), no more and no less.\n"
            f"2. Each script MUST be {LENGTH_OF_SCRIPT_IN_SECONDS} seconds long when narrated as audio.\n"
            f"3. Use simple yet effective language that is attractive, meaningful, and maintains narrative flow across all scripts.\n"
            f"4. Each script should correspond to its specific chapter and maintain logical coherence with both its chapter and the overall story arc.\n"
            f"5. The scripts will be used to generate images, video, and audio to tell the story, so they must be clear, descriptive, and visually evocative.\n"
            f"6. Ensure smooth transitions between scripts within the same chapter and maintain consistency with the events of the corresponding chapter.\n\n"
            f"Return a JSON with keys: scripts."
        )
        chapters_data = [chapter.model_dump() for chapter in primary_result.chapters]
        resp = self.t2t.generate(
            system_prompt=system_prompt,
            user_prompt=f"Theme: {primary_result.title}, chapters={chapters_data}",
            output_type=Scripts
        )
        try:
            return resp
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini output: {e}")
    
    def translate(self,scripts: Scripts, lang: str) -> Scripts:
        """
        Translates the script to the given language

        Args:
            scripts (Scripts): scripts in English
            lang (str): target language 

        Returns:
            Scripts: translated scripts
        """

        system_prompt = """You are a culturally sensitive translation model.
Your task is to translate a list of Indic-origin mythical and folktale scripts from English to a target Indian language specified by the user.
Maintain the natural flow and readability of the target language.
Preserve the emotional tone, rhythm, and narrative style of the original.
Respect the mythical and folkloric context—do not modernize or rationalize the content.
Avoid literal translations if they result in awkward or unnatural phrasing.
Use culturally appropriate idioms, expressions, and traditional language patterns.
For example, using honorary plural forms etc.
Do not add, remove, or alter story elements beyond what is necessary for natural translation.
The input and output follow the format: class Scripts(BaseModel): scripts: List[str].
Return only the translated scripts in the same structure."""     

        try:
            translated_scripts = self.t2t.generate(
                system_prompt=system_prompt,
                user_prompt= f"Target Language: {lang}",
                output_type=Scripts,
                input_data=scripts
            )
            return translated_scripts
        except  Exception as e:
            raise ValueError(f"Failed to translate: {e}")
