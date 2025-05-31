from hindutales.core.story_guru import StoryGuru
from hindutales.core.prompt_guru import PromptGuru
from hindutales.core.video_gen import VideoGen
from hindutales.types.main import VideoGenInput, VideoMakerParams, VideoMakerResult, AudioMakerParams, AudioMakerResult
from hindutales.core.image_maker import ImageMaker
from hindutales.core.audio_maker import AudioMaker
from pathlib import Path
import json
import shutil
import re

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

        audio_maker = AudioMaker(
            params=AudioMakerParams(
                paras=scripts.scripts,
                lang=self.lang,
                duration=self.duration
            )
        )
        audios = audio_maker.generate()

        images = ImageMaker.generate(image_prompts.prompts)

        # all_video_inputs = []
        # for i in range(len(images)):
            # all_video_inputs.append(VideoGenInput(image_path=images[i], video_prompt=video_prompts.prompts[i]))

        # video_gen = VideoGen.create_video(all_video_inputs)


        def sanitize_filename(name: str) -> str:
            return re.sub(r'[^\w\-]', '_', name)

        save_dir: Path = Path('output') / sanitize_filename(self.title)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save LLM-generated data
        with open(save_dir / 'primary_result.json', 'w', encoding='utf-8') as f:
            json.dump(primary_result.__dict__ if hasattr(primary_result, '__dict__') else dict(primary_result), f, ensure_ascii=False, indent=2)
        with open(save_dir / 'scripts.json', 'w', encoding='utf-8') as f:
            json.dump(scripts.scripts, f, ensure_ascii=False, indent=2)
        with open(save_dir / 'image_prompts.json', 'w', encoding='utf-8') as f:
            json.dump(image_prompts.__dict__ if hasattr(image_prompts, '__dict__') else dict(image_prompts), f, ensure_ascii=False, indent=2)
        with open(save_dir / 'video_prompts.json', 'w', encoding='utf-8') as f:
            json.dump(video_prompts.__dict__ if hasattr(video_prompts, '__dict__') else dict(video_prompts), f, ensure_ascii=False, indent=2)

        # Save images (copy from images/uuid.png to save_dir)
        images_dir = Path('images')
        for idx, image_uuid in enumerate(images):
            src_path = images_dir / f'{image_uuid}.png'
            dst_path = save_dir / f'image_{idx+1}.png'
            if src_path.exists():
                shutil.copy2(src_path, dst_path)

        # Save audios (BytesIO)
        for idx, audio_io in enumerate(audios):
            audio_path = save_dir / f'audio_{idx+1}.mp3'
            with open(audio_path, 'wb') as f:
                f.write(audio_io.getbuffer())

        return VideoMakerResult(
            title=primary_result.title,
            chapters=primary_result.chapters,
            scripts=scripts.scripts,
            image_prompts=image_prompts,
            video_prompts=video_prompts,
            lang=self.lang
        )
