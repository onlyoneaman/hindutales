from typing import List
from hindutales.nodes.agents.t2t.t2t import T2TConverter
from hindutales.types.main import PrimaryResult, Scripts, Message

# story -> chapters -> scripts, videos
LENGTH_OF_STORY_IN_SECONDS = 60
NUMBER_OF_CHAPTERS_PER_STORY = 4
NUMBER_OF_SCRIPTS_PER_CHAPTER = 1
NUMBER_OF_VIDEOS_PER_CHAPTER = 1
LENGTH_OF_SCRIPT_IN_SECONDS = LENGTH_OF_STORY_IN_SECONDS / (NUMBER_OF_CHAPTERS_PER_STORY * NUMBER_OF_SCRIPTS_PER_CHAPTER)


class StoryGuru:
    def __init__(self):
        pass
        self.t2t = T2TConverter(
            model="gpt-4o",
            temperature=0.8,
            top_p=0.9
        )

    def generate_outline(self, title: str, lang: str):
        """
        Goals:
        1. break down story in such parts where the total story can be of length 1-1.5 minutes
        2. the stories should be factually correct and cohenerent with indian mythology.
        """
        system_prompt = (
            f"You are a creative short-form video writer and story writer expert. Your goal is to create a {LENGTH_OF_STORY_IN_SECONDS} seconds long YouTube Short or Instagram Reel that is engaging, entertaining, and educational. The stories mostly will be related to indian mythology"
            f"Given a prompt, generate: "
            f"1. A title for the video that will be story's title."
            f"2. Outline of the video in chapters. Chapter should be divided such that, conceptually, to describe that chapter in both audio and video format should be almost equal. Keep chapter title short"
            f"3. there should be exactly {NUMBER_OF_CHAPTERS_PER_STORY} chapters for the given story." 
            f"Return a JSON with keys: title, chapters."
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
            f"You are a creative short-form video writer expert. Your goal is to create scripts for chapters of a story."
            f"Given an array of chapters that form an entire story when told together, you will generate scripts for each chapter."
            f"Requirements:\n"
            f"1. Generate EXACTLY {NUMBER_OF_CHAPTERS_PER_STORY * NUMBER_OF_SCRIPTS_PER_CHAPTER} total scripts for the given story, no more and no less.\n"
            f"2. Each script MUST be {LENGTH_OF_SCRIPT_IN_SECONDS} seconds long when narrated as audio.\n"
            f"3. Use simple yet effective language that is attractive, meaningful, and coherent with the entire story.\n"
            f"4. The scripts must be logically coherent with the overall story narrative.\n"
            f"5. The scripts will be used to generate images, video, and audio to tell the story, so they must be clear and descriptive.\n"
            f"Return a JSON with keys: scripts."
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