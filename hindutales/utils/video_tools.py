import os
import ffmpeg
from decimal import Decimal
from elevenlabs import ForcedAlignmentResponseModel

from hindutales.utils.ass_utils import generate_ass_file
from hindutales.utils.audio_utils import get_audio_length

def get_video_dimensions(path):
    probe = ffmpeg.probe(path)
    videoStream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(videoStream['width'])
    height = int(videoStream['height'])
    return width, height

def check_video_length(video_path):
    video_length = get_video_length(video_path)
    video_codec_length = get_video_codec_length(video_path)
    if video_length != video_codec_length:
        # print warning
        print(f"Video and codec lengths do not match: {video_length} != {video_codec_length}")
    print(f"Video length: {video_length}")
    return video_length

def get_video_length(path):
    probe = ffmpeg.probe(path)
    duration = float(probe['format']['duration'])
    return duration

def print_durations(file_path):
    video_length = get_video_length(file_path)
    video_codec_length = get_video_codec_length(file_path)
    audio_length = get_audio_length(file_path)
    print(f"Video length: {video_length}")
    print(f"Video codec length: {video_codec_length}")
    print(f"Audio codec length: {audio_length}")

def get_video_codec_length(path):
    probe = ffmpeg.probe(path)
    videoStream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    duration = float(videoStream['duration'])
    return duration
    
def is_valid_aspect_ratio(width, height, aspect_ratio=9/16):
    aspect_ratio = width / height
    return aspect_ratio == aspect_ratio

def file_exists(path):
    return os.path.exists(path)

def is_valid_video(path, aspect_ratio=9/16):
    if not file_exists(path):
        raise ValueError(f"File {path} does not exist")
    width, height = get_video_dimensions(path)
    return is_valid_aspect_ratio(width, height, aspect_ratio)

def add_padding(video_path, output_path, aspect_ratio=9/16, padding_color=(0, 0, 0)):
    if not file_exists(video_path):
        raise ValueError(f"File {video_path} does not exist")
    width, height = get_video_dimensions(video_path)
    if is_valid_aspect_ratio(width, height, aspect_ratio):
        return
    
    padding = (height * aspect_ratio - width) // 2
    ffmpeg.input(video_path).filter('pad', width=width+padding, height=height, color=padding_color).output(output_path).run()
    
    return output_path

def video_to_target_dimensions(
    path: str, 
    output_path: str,
    target_width: int = 720,
    target_height: int = 1280,
    ) -> str:
    if not file_exists(path):
        raise ValueError(f"File {path} does not exist")
    # add padding if needed
    width, height = get_video_dimensions(path)

    scale = target_width / width
    scaled_height = int(height * scale)

    if scaled_height > target_height:
        scale = target_height / height
        scaled_width = int(width * scale)
        pdX = (target_width - scaled_width) // 2
        pdY = 0
    else:
        scaled_width = target_width
        pdX = 0
        pdY = (target_height - scaled_height) // 2

    output = ffmpeg.input(path).filter('pad', width=target_width, height=target_height, x=pdX, y=pdY).output(output_path)
    ffmpeg.run(output, overwrite_output=True, quiet=True)
    return output_path

def create_segments(
    image_paths: list[str],
    audio_paths: list[str],
    dir_name: str,
    framerate: int = 30,
):
    segment_paths = []
    os.makedirs(dir_name, exist_ok=True)
    
    num_images = len(image_paths)
    num_audios = len(audio_paths)
    
    if num_images >= num_audios:
        # Split each audio across multiple images
        for audio_idx, aud_path in enumerate(audio_paths):
            info = ffmpeg.probe(aud_path)
            total_duration = Decimal(info["format"]["duration"])
            
            # Calculate how many images this audio should span
            images_per_audio = num_images // num_audios
            remainder = num_images % num_audios
            extra_image = 1 if audio_idx < remainder else 0
            num_images_for_audio = images_per_audio + extra_image
            
            duration_per_image = total_duration / num_images_for_audio
            
            start_img_idx = audio_idx * images_per_audio + min(audio_idx, remainder)
            
            for i in range(num_images_for_audio):
                img_idx = start_img_idx + i
                img_path = image_paths[img_idx]
                
                start_time = i * duration_per_image
                segment_path = os.path.join(dir_name, f"segment_{img_idx}.mp4")
                
                img_stream = ffmpeg.input(img_path, loop=1, t=duration_per_image, framerate=framerate)
                aud_stream = ffmpeg.input(aud_path, ss=float(start_time), t=float(duration_per_image))
                
                (
                    ffmpeg
                    .output(
                        img_stream,
                        aud_stream,
                        segment_path,
                        vcodec="libx264",
                        acodec="aac",
                        pix_fmt="yuv420p"
                    )
                    .run(quiet=True, overwrite_output=True)
                )
                segment_paths.append(segment_path)
    else:
        # Each image gets multiple audio files
        for img_idx, img_path in enumerate(image_paths):
            # Calculate how many audios this image should span
            audios_per_image = num_audios // num_images
            remainder = num_audios % num_images
            extra_audio = 1 if img_idx < remainder else 0
            num_audios_for_image = audios_per_image + extra_audio
            
            start_aud_idx = img_idx * audios_per_image + min(img_idx, remainder)
            
            for i in range(num_audios_for_image):
                aud_idx = start_aud_idx + i
                aud_path = audio_paths[aud_idx]
                
                info = ffmpeg.probe(aud_path)
                duration = Decimal(info["format"]["duration"])
                
                segment_path = os.path.join(dir_name, f"segment_{aud_idx}.mp4")
                
                img_stream = ffmpeg.input(img_path, loop=1, t=duration, framerate=framerate)
                aud_stream = ffmpeg.input(aud_path)
                
                (
                    ffmpeg
                    .output(
                        img_stream,
                        aud_stream,
                        segment_path,
                        vcodec="libx264",
                        acodec="aac",
                        pix_fmt="yuv420p"
                    )
                    .run(quiet=True, overwrite_output=True)
                )
                segment_paths.append(segment_path)
    
    return segment_paths

def add_subtitles(
    video_path: str,
    forced_alignment: ForcedAlignmentResponseModel,
    output_path: str,
    target_width: int = 720,
    target_height: int = 1280,
):
    """
    Adds subtitles to a video using forced alignment.
    """
    print("Adding subtitles to video...")
    words = forced_alignment.words
    ass_path = "subtitles.ass"
    ass_full_path = os.path.join(os.path.dirname(video_path), ass_path)
    generate_ass_file(
        words=words,
        output_path=ass_full_path,
        target_width=target_width,
        target_height=target_height
    )
    print(f"Generated subtitles at {ass_full_path}")
    output = (
        ffmpeg
        .input(video_path)
        .output(output_path, vf=f"ass={ass_full_path}", vcodec="libx264", acodec="aac")
    )
    ffmpeg.run(output, overwrite_output=True, quiet=True)
