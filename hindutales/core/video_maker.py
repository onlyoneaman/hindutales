from hindutales.core.story_guru import StoryGuru
from hindutales.core.prompt_guru import PromptGuru
from hindutales.types.main import VideoMakerParams, VideoMakerResult, AudioMakerParams, AudioMakerResult
from hindutales.core.image_maker import ImageMaker
from hindutales.core.audio_maker import AudioMaker
from hindutales.core.utils import create_audio_image_pairs

import time
from pathlib import Path
import json
import shutil
import re
import glob
from pathlib import Path
import ffmpeg
from hindutales.utils.fs_utils import sanitize_filename

class VideoMaker:
    def __init__(self, params: VideoMakerParams) -> None:
        self.title: str = params.title
        self.description: str = params.description
        self.lang: str = params.lang
        self.duration: int = params.duration
        self.story_guru = StoryGuru()
        self.prompt_guru = PromptGuru()

    def generate(self) -> VideoMakerResult:
        print("1. Generating outline")
        step_start: float = time.perf_counter()
        primary_result = self.story_guru.generate_outline(self.title, self.description)
        print(f"Step 1 done in {time.perf_counter() - step_start:.2f} seconds.")

        timestamp: str = time.strftime("%Y%m%d_%H%M%S")
        save_dir: Path = Path('output') / sanitize_filename(self.title + "_" + self.lang + "_" + timestamp)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save LLM-generated data
        with open(save_dir / 'primary_result.json', 'w', encoding='utf-8') as f:
            json.dump(primary_result.model_dump(), f, ensure_ascii=False, indent=2)

        print("2. Generating scripts")
        step_start = time.perf_counter()
        scripts = self.story_guru.generate_scripts(primary_result, self.lang)
        print(f"Step 2 done in {time.perf_counter() - step_start:.2f} seconds.")

        with open(save_dir / 'scripts.json', 'w', encoding='utf-8') as f:
            json.dump(scripts.model_dump(), f, ensure_ascii=False, indent=2)

        print("3. Generating image prompts")
        step_start = time.perf_counter()
        image_prompts = self.prompt_guru.get_image_prompts(self.title, primary_result.chapters, scripts.scripts)
        print(f"Step 3 done in {time.perf_counter() - step_start:.2f} seconds.")
        # video_prompts = self.prompt_guru.get_video_prompts(self.title, primary_result.chapters, scripts.scripts)

        with open(save_dir / 'image_prompts.json', 'w', encoding='utf-8') as f:
            json.dump(image_prompts.model_dump(), f, ensure_ascii=False, indent=2)
        # with open(save_dir / 'video_prompts.json', 'w', encoding='utf-8') as f:
            # json.dump(video_prompts.model_dump(), f, ensure_ascii=False, indent=2)

        print("4. Generating audio")

        narration_script = scripts.scripts

        if self.lang.lower() != "english":
            print(f"4.1 Translating language to {self.lang}")
            step_start = time.perf_counter()  # Start performance timer
            narration_script = self.story_guru.translate(scripts=scripts, lang=self.lang)
            with open(save_dir / 'translated_narration_script.json', 'w', encoding='utf-8') as f:
                json.dump(narration_script.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"Step 4.1 done in {time.perf_counter() - step_start:.2f} seconds.")  # Log duration

        step_start = time.perf_counter()
        audio_maker = AudioMaker(
            params=AudioMakerParams(
                paras=narration_script.scripts,
                lang=self.lang,
                duration=self.duration
            )
        )
        
        audios = audio_maker.generate()
        print(f"Step 4 done in {time.perf_counter() - step_start:.2f} seconds.")

        print("5. Generating images")
        step_start = time.perf_counter()
        images = ImageMaker.generate(image_prompts.prompts)
        print(f"Step 5 done in {time.perf_counter() - step_start:.2f} seconds.")

        images_dir: Path = Path('images')
        for idx, image_uuid in enumerate(images):
            src_path: Path = images_dir / f'{image_uuid}.png'
            dst_path: Path = save_dir / f'image_{idx+1}.png'
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
        for idx, audio_io in enumerate(audios):
            audio_path: Path = save_dir / f'audio_{idx+1}.mp3'
            with open(audio_path, 'wb') as f:
                f.write(audio_io.getbuffer())

        return VideoMakerResult(
            title=primary_result.title,
            description=primary_result.description,
            chapters=primary_result.chapters,
            scripts=scripts.scripts,
            image_prompts=image_prompts,
            # video_prompts=video_prompts,
            lang=self.lang,
            timestamp=timestamp
        )

    def save_video(self, result: VideoMakerResult, title: str) -> None:
        save_dir: Path = Path('output') / sanitize_filename(title + "_" + result.lang + "_" + result.timestamp)
        save_dir.mkdir(parents=True, exist_ok=True)
        video_path: Path = save_dir / f'{title}.mp4'
        input_dir = save_dir
        # input_dir: Path = Path(result.input_dir) if hasattr(result, 'input_dir') else Path('.')

        audio_files: list[str] = sorted(glob.glob(str(input_dir / 'audio_*.mp3')))
        image_files: list[str] = sorted(glob.glob(str(input_dir / 'image_*.png')))

        def extract_index(filename: str) -> int:
            match = re.search(r'_(\d+)\.', filename)
            return int(match.group(1)) if match else -1

        audio_list = sorted(audio_files, key=extract_index)
        image_list = sorted(image_files, key=extract_index)

        paired_files = create_audio_image_pairs(audio_list, image_list)
        segment_files: list[Path] = []

        # audio_dict = {extract_index(f): f for f in audio_files if extract_index(f) != -1}
        # image_dict = {extract_index(f): f for f in image_files if extract_index(f) != -1}

        # common_indices = sorted(set(audio_dict) & set(image_dict))
        # missing_audio = sorted(set(image_dict) - set(audio_dict))
        # missing_image = sorted(set(audio_dict) - set(image_dict))
        # for idx in missing_audio:
        #     print(f"Warning: Missing audio file for image index {idx}")
        # for idx in missing_image:
        #     print(f"Warning: Missing image file for audio index {idx}")
        # if not common_indices:
        #     raise ValueError("No matching audio/image index pairs found.")
        # paired_files = [(audio_dict[i], image_dict[i]) for i in common_indices]
        # segment_files: list[Path] = []

        # Step 1: Generate video segments for each image/audio pair

        print(f"Generating video segments for {len(paired_files)} pairs")
        print(f"Joined video segments: {paired_files}")

        for idx, pair in enumerate(paired_files, 1):
            # Get audio duration using ffmpeg.probe
            audio, image, duration = pair
            probe = ffmpeg.probe(audio)
            duration: float = float(probe['format']['duration'])
            segment_path: Path = save_dir / f'segment_{idx}.mp4'
            segment_files.append(segment_path)

            stream_img = ffmpeg.input(image, loop=1, t=duration)
            stream_aud = ffmpeg.input(audio)

            stream = ffmpeg.output(
                stream_img,
                stream_aud.audio.filter('aformat', channel_layouts='stereo', sample_rates=44100),
                str(segment_path),
                vcodec='libx264',
                acodec='aac',
                ac=2,
                ar=44100,
                pix_fmt='yuv420p',
                shortest=None,
                t=duration,
                y=None
            )
            stream.run(overwrite_output=True, quiet=False)

        # Step 2: Concatenate all segments
        if not segment_files:
            raise ValueError("No video segments were created. Check that your audio/image files are valid.")
        # Filter segment files to only those with both video and audio streams
        valid_segment_files = []
        for seg in segment_files:
            probe = ffmpeg.probe(str(seg))
            has_video = any(s['codec_type'] == 'video' for s in probe['streams'])
            has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])
            if has_video and has_audio:
                valid_segment_files.append(seg)
            else:
                print(f"Warning: Skipping {seg} (missing video or audio stream)")
        if not valid_segment_files:
            raise ValueError("No valid video segments with both video and audio streams found.")

        # FIXED: Use correct ffmpeg-python concatenation approach
        if len(valid_segment_files) == 1:
            # If only one segment, just copy it
            shutil.copy2(valid_segment_files[0], video_path)
        else:
            # Create a concat file for ffmpeg
            concat_file = save_dir / 'concat_list.txt'
            with open(concat_file, 'w') as f:
                for seg in valid_segment_files:
                    f.write(f"file '{seg.resolve()}'\n")
            
        (
            ffmpeg
            .input(str(concat_file), format='concat', safe=0)
            .output(str(video_path), c='copy')
            .run(overwrite_output=True, quiet=False)
        )

        # Step 3: Clean up segment files
        for segment in segment_files:
            segment.unlink(missing_ok=True)
