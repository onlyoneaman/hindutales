import os
import json
import argparse
import traceback
from io import BytesIO
from datetime import datetime
from elevenlabs import ForcedAlignmentResponseModel

from directors_house import (
    get_story_outline, create_scripts, create_image_prompts,
    create_images, create_audios, get_forced_alignment
)
from hindutales.models.video import StoryOutput, VideoMakerResult, ScriptsOutput
from hindutales.utils.audio_utils import merge_audio
from hindutales.utils.fs_utils import sanitize_filename, make_dirs, save_to_file
from hindutales.utils.video_tools import create_segments, add_subtitles, check_video_length, print_durations

from finalize_videos import finalize_videos

VIDEOGEN_DIR = "tmp/videogens"

TARGET_WIDTH = 720
TARGET_HEIGHT = 1280

# create a single json to store all the results store images, audios if present in the same directory and store paths in json
def save_results(
    out_dir: str,
    story_output: StoryOutput,
    scripts_output: ScriptsOutput,
    image_prompts: list[str],
    image_bytes: list[bytes],
    audio_buffers: list[BytesIO],
):
    raw_dir = os.path.join(out_dir, "raw")
    make_dirs([out_dir, raw_dir])
    image_paths = []
    for i, image_bytes in enumerate(image_bytes):
        image_path = os.path.join(raw_dir, f"image_{i}.png")
        save_to_file(
            content=image_bytes,
            path=image_path,
            mode="wb"
        )
        image_paths.append(image_path)
    audio_paths = []
    for i, audio_buffer in enumerate(audio_buffers):
        audio_path = os.path.join(raw_dir, f"audio_{i}.mp3")
        save_to_file(
            content=audio_buffer.getvalue(),
            path=audio_path,
            mode="wb"
        )
        audio_paths.append(audio_path)
    final_json = {
        "story": story_output.model_dump_json(),
        "scripts": scripts_output.model_dump_json(),
        "image_prompts": image_prompts,
        "image_paths": image_paths,
        "audio_paths": audio_paths,
    }
    final_json_file = os.path.join(out_dir, "final.json")
    final_json = json.dumps(final_json)
    save_to_file(
        content=final_json,
        path=final_json_file,
        mode="w"
    )
    print(f"Saved final.json to {final_json_file}")


def create_video_raw_config(
    topic: str,
    description: str,
    duration_seconds: int,
    lang: str,
) -> str:
    """
    Input: 
    topic: str
    description: str
    duration_seconds: int

    Output: 
    video_path: str
    """
    try:
        start_time = datetime.now()

        dir_name = f"{sanitize_filename(topic)}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        out_dir = f"{VIDEOGEN_DIR}/{dir_name}"
        os.makedirs(out_dir, exist_ok=True)

        # 1. Create Title, Subtitle, and Outline
        func_start_time = datetime.now()
        user_approved = False
        while not user_approved:
            story_output = get_story_outline(
                prompt=topic, 
                description=description, 
                duration_seconds=duration_seconds,
                lang=lang
            )
            print("Story outline generated")
            print(f"Story: {story_output.story}")
            print(f"Outline: {story_output.outline}")
            print(f"Title: {story_output.title}")
            print(f"Description: {story_output.description}")
            print("---------------")
            user_approved = input("Approved? (y/n): (Press Enter to regenerate)")
            if user_approved.lower() == "y":
                user_approved = True
            else:
                user_approved = False
        func_end_time = datetime.now()
        print(f"[get_story_outline]: {(func_end_time - func_start_time).total_seconds()}s")

        # 2. Create Subtitles
        func_start_time = datetime.now()
        user_approved = False
        while not user_approved:
            scripts_output = create_scripts(
                output=story_output,
                duration_seconds=duration_seconds,
                lang=lang
            )
            print("Scripts generated")
            print(f"Scripts: {scripts_output.scripts}")
            print("---------------")
            user_approved = input("Approved? (y/n): (Press Enter to regenerate)")
            if user_approved.lower() == "y":
                user_approved = True
            else:
                user_approved = False
        func_end_time = datetime.now()
        print(f"[create_scripts]: {(func_end_time - func_start_time).total_seconds()}s")

        # 3. Create Image prompts
        func_start_time = datetime.now()
        image_prompts_output = create_image_prompts(
            story=story_output, 
            scripts=scripts_output, 
            duration_seconds=duration_seconds
        )
        func_end_time = datetime.now()
        print(f"[create_image_prompts]: {(func_end_time - func_start_time).total_seconds()}s")
        image_prompts = image_prompts_output.image_prompts

        # 4. Create Images for each parts
        func_start_time = datetime.now()
        image_bytes = create_images(image_prompts)
        func_end_time = datetime.now()
        print(f"[create_images]: {(func_end_time - func_start_time).total_seconds()}s")

        # 5. Create Audios
        func_start_time = datetime.now()
        audio_buffers = create_audios(scripts_output.scripts)
        func_end_time = datetime.now()
        print(f"[create_audios]: {(func_end_time - func_start_time).total_seconds()}s")

        # 6. Save all results and files and create config
        func_start_time = datetime.now()

        print(f"Saving results to {out_dir}")

        save_results(
            out_dir=out_dir,
            story_output=story_output,
            scripts_output=scripts_output,
            image_prompts=image_prompts,
            image_bytes=image_bytes,
            audio_buffers=audio_buffers,
        )
        func_end_time = datetime.now()
        print(f"[save_results]: {(func_end_time - func_start_time).total_seconds()}s")
        return dir_name
    except Exception as e:
        print(f"Error: {e}, {traceback.format_exc()}")
        return None

def final_subtitles(
    results: VideoMakerResult,
    output_dir: str,
): 
    output_dir_path = os.path.join(VIDEOGEN_DIR, output_dir)
    audio_paths = results.audio_paths
    scripts = results.scripts
    forced_alignment_filename = "forced_alignment.json"

    # [TODO]: Can be replaced with local whisper

    # check if file exists then skip
    forced_alignment_path = os.path.join(output_dir_path, forced_alignment_filename)
    if os.path.exists(forced_alignment_path):
        print(f"Forced alignment already exists at {forced_alignment_path}")
        # regenerate forced alignment
        regenerate = input("Regenerate forced alignment? (y/n): (Press Enter to skip) ")
        if regenerate.lower() == "y":
            os.remove(forced_alignment_path)
        else:
            forced_alignment_details = json.load(open(forced_alignment_path, "r"))
            return ForcedAlignmentResponseModel(**forced_alignment_details)

    # 7. create full length audio
    full_audio_path = os.path.join(output_dir_path, "full_audio.mp3")
    merge_audio(audio_paths, full_audio_path)

    # 8. get forced transcript
    forced_alignment = get_forced_alignment(full_audio_path, scripts.scripts)

    forced_alignment_path = os.path.join(output_dir_path, forced_alignment_filename)
    save_to_file(
        content=forced_alignment.model_dump_json(),
        path=forced_alignment_path,
        mode="w"
    )

    return forced_alignment

def mix_final_video(
    results: VideoMakerResult,
    dir_name: str,
    forced_alignment: ForcedAlignmentResponseModel,
) -> str:
    """
    Mix images and audios into a single reel-style video with optional transitions.

    Args:
        results: VideoMakerResult containing image_paths and audio_paths.
    """
    image_paths = results.image_paths
    audio_paths = results.audio_paths
    print(f"Received {len(image_paths)} images and {len(audio_paths)} audios")

    output_dir = os.path.join(VIDEOGEN_DIR, dir_name)
    merged_path = os.path.join(output_dir, f"merged.mp4")
    final_path = os.path.join(output_dir, f"final.mp4")
    remerge = False

    if os.path.exists(merged_path):
        overwrite = input(f"Merged video already exists at {merged_path}. Overwrite? (y/n): ")
        if overwrite.lower() == "y" or overwrite.lower() == "yes":
            os.remove(merged_path)
            remerge = True
        else:
            remerge = False
    else:
        remerge = True

    if remerge:
        # create segments
        segments = create_segments(
            image_paths=image_paths,
            audio_paths=audio_paths,
            dir_name=output_dir,
        )

        # 9. pad and merge
        finalize_videos(
            video_paths=segments,
            output_path=merged_path,
            target_width=TARGET_WIDTH,
            target_height=TARGET_HEIGHT,
            transition="simple"
        )

        # clear segments
        for segment in segments:
            os.remove(segment)    

    check_video_length(merged_path)

    # 10. add subtitles
    add_subtitles(
        video_path=merged_path,
        forced_alignment=forced_alignment,
        output_path=final_path,
        target_width=TARGET_WIDTH,
        target_height=TARGET_HEIGHT
    )

    # 11. create final cover

    print(f"Final reel video created at {final_path}")
    return final_path

def load_results(out_dir: str) -> VideoMakerResult:
    out_dir = os.path.join(VIDEOGEN_DIR, out_dir)
    final_json_file = os.path.join(out_dir, "final.json")
    results = json.load(open(final_json_file, "r"))
    story_output_json = json.loads(results["story"])
    story_output = StoryOutput(**story_output_json)
    scripts_output_json = json.loads(results["scripts"])
    scripts_output = ScriptsOutput(**scripts_output_json)
    image_prompts = results["image_prompts"]
    image_paths = results["image_paths"]
    audio_paths = results["audio_paths"]
    print(f"Title: {story_output.title}")
    print(f"Description: {story_output.description}")
    print(f"Story: {story_output.story}")
    outline = story_output.outline
    for i, part in enumerate(outline):
        print(f"Part {i+1}: {part}")
    print(f"Total Outline Parts: {len(story_output.outline)}")
    print(f"Scripts: {scripts_output.scripts}")
    print("no. of images: ", len(image_prompts))
    for i, image_prompt in enumerate(image_prompts):
        print(f"Image {i+1}: {image_prompt}")
    print("no. of scripts: ", len(scripts_output.scripts))
    print("no. of image paths: ", len(image_paths))
    print("no. of audio paths: ", len(audio_paths))
    final_results = VideoMakerResult(
        story=story_output,
        scripts=scripts_output,
        image_prompts=image_prompts,
        image_paths=image_paths,
        audio_paths=audio_paths,
    )
    return final_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_name", type=str, required=False)
    parser.add_argument("--topic", type=str, required=False)
    parser.add_argument("--description", type=str, required=False)
    parser.add_argument("--duration_seconds", type=int, default=60, required=False)
    parser.add_argument("--lang", type=str, required=False)
    args = parser.parse_args()
    dir_name = args.dir_name
    topic = args.topic
    description = args.description
    duration_seconds = args.duration_seconds
    lang = args.lang
    start_time = datetime.now()

    if not dir_name:
        dir_name = input("Enter dir name (empty to create new): ")
        if not dir_name:
            topic = topic or input("Enter topic: ")
            description = description or input("Enter description: ")
            duration_seconds = duration_seconds or 60
            lang = lang or input("Enter language: (english) ")
            if not lang:
                lang = "english"
            dir_name = create_video_raw_config(
                topic=topic,
                description=description,
                duration_seconds=duration_seconds,
                lang=lang,
            )
    if not dir_name:
        print("No dir name provided. Some error occurred. Please try again.")
        exit()
    print(f"Results saved to {dir_name}")

    results = load_results(dir_name)

    forced_alignment = final_subtitles(
        results=results,
        output_dir=dir_name,
    )

    # mix video
    output_path = mix_final_video(
        results=results,
        dir_name=dir_name,
        forced_alignment=forced_alignment,
    )

    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time.total_seconds()}s")
    
