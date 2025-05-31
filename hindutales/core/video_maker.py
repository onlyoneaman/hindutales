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
import time

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-]', '_', name)

class VideoMaker:
    def __init__(self, params: VideoMakerParams) -> None:
        self.title: str = params.title
        self.lang: str = params.lang
        self.duration: int = params.duration
        self.story_guru = StoryGuru()
        self.prompt_guru = PromptGuru()

    def generate(self) -> VideoMakerResult:
        primary_result = self.story_guru.generate_outline(self.title, self.lang)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_dir: Path = Path('output') / sanitize_filename(self.title + "_" + self.lang + "_" + timestamp)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save LLM-generated data
        with open(save_dir / 'primary_result.json', 'w', encoding='utf-8') as f:
            json.dump(primary_result.model_dump(), f, ensure_ascii=False, indent=2)

        scripts = self.story_guru.generate_scripts(primary_result)

        with open(save_dir / 'scripts.json', 'w', encoding='utf-8') as f:
            json.dump(scripts.model_dump(), f, ensure_ascii=False, indent=2)

        image_prompts = self.prompt_guru.get_image_prompts(self.title, primary_result.chapters, scripts.scripts)
        video_prompts = self.prompt_guru.get_video_prompts(self.title, primary_result.chapters, scripts.scripts)

        with open(save_dir / 'image_prompts.json', 'w', encoding='utf-8') as f:
            json.dump(image_prompts.model_dump(), f, ensure_ascii=False, indent=2)
        with open(save_dir / 'video_prompts.json', 'w', encoding='utf-8') as f:
            json.dump(video_prompts.model_dump(), f, ensure_ascii=False, indent=2)

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
