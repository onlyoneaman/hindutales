from hindutales.core.story_guru import StoryGuru
from hindutales.types.main import VideoMakerParams, VideoMakerResult, PrimaryResult

class VideoMaker:
    def __init__(self, params: VideoMakerParams) -> None:
        self.title: str = params.title
        self.lang: str = params.lang
        self.duration: int = params.duration
        self.story_guru = StoryGuru()

    def generate(self) -> VideoMakerResult:
        primary_result = self.generate_primary_result()
        return VideoMakerResult(
            title=primary_result.title,
            chapters=primary_result.chapters,
            lang=self.lang
        )

    def generate_primary_result(self) -> PrimaryResult:
        outline = self.story_guru.generate_outline(self.title, self.lang)
        return outline