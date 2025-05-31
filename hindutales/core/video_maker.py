from hindutales.core.story_guru import StoryGuru
from hindutales.core.prompt_guru import PromptGuru
from hindutales.types.main import VideoMakerParams, VideoMakerResult
from hindutales.core.image_maker import ImageMaker

class VideoMaker:
    def __init__(self, params: VideoMakerParams) -> None:
        self.title: str = params.title
        self.lang: str = params.lang
        self.duration: int = params.duration
        self.story_guru = StoryGuru()
        self.prompt_guru = PromptGuru()

    def generate(self) -> VideoMakerResult:
        primary_result = self.story_guru.generate_outline(self.title, self.lang)
        scripts = self.story_guru.generate_scripts(primary_result)
        image_prompts = self.prompt_guru.get_image_prmopts(self.title, primary_result.chapters, scripts.scripts)

        images = ImageMaker.generate(image_prompts.prompts)

        return VideoMakerResult(
            title=primary_result.title,
            chapters=primary_result.chapters,
            scripts=scripts.scripts,
            image_prompts=image_prompts,
            lang=self.lang
        )
