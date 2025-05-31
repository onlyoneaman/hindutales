from hindutales.core.story_guru import StoryGuru
from hindutales.core.prompt_guru import PromptGuru
from hindutales.core.video_gen import VideoGen
from hindutales.types.main import VideoGenInput, VideoMakerParams, VideoMakerResult
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
        video_prompts = self.prompt_guru.get_video_prompts(self.title, primary_result.chapters, scripts.scripts)

        images = ImageMaker.generate(image_prompts.prompts)

        all_video_inputs = []
        for i in range(len(images)):
            all_video_inputs.append(VideoGenInput(image_path=images[i], video_prompt=video_prompts.prompts[i]))

        video_gen = VideoGen.create_video(all_video_inputs)

        return VideoMakerResult(
            title=primary_result.title,
            chapters=primary_result.chapters,
            scripts=scripts.scripts,
            image_prompts=image_prompts,
            video_prompts=video_prompts,
            lang=self.lang
        )
