from hindutales.core.story_guru import StoryGuru
from hindutales.types.main import VideoMakerParams, VideoMakerResult

class VideoMaker:
    def __init__(self, params: VideoMakerParams) -> None:
        self.title: str = params.title
        self.lang: str = params.lang
        self.duration: int = params.duration
        self.story_guru = StoryGuru()

    def generate(self) -> VideoMakerResult:
        primary_result = self.story_guru.generate_outline(self.title, self.lang)
        scripts = self.story_guru.generate_scripts(primary_result)
        return VideoMakerResult(
            title=primary_result.title,
            chapters=primary_result.chapters,
            scripts=scripts.scripts,
            lang=self.lang
        )
