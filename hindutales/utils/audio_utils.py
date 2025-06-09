import ffmpeg
import tempfile
import os

def get_audio_length(path: str) -> float:
    probe = ffmpeg.probe(path)
    audioStream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    duration = audioStream['duration']
    if duration is None:
        raise ValueError(f"Audio duration not found for {path}")
    return float(duration)


def merge_audio(audio_paths: list[str], output_path: str):
    """Merge multiple audio files into a single output file.
    
    Args:
        audio_paths: List of paths to audio files to merge
        output_path: Path to save the merged audio file
    """
    if not audio_paths:
        raise ValueError("No audio paths provided")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        for path in audio_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Audio file not found: {path}")
            temp_file.write(f"file '{os.path.abspath(path)}'\n")
        temp_file_path = temp_file.name
    
    try:
        ffmpeg.input(temp_file_path, format='concat', safe=0).output(
            output_path, acodec='libmp3lame', audio_bitrate='192k'
        ).run(quiet=True, overwrite_output=True)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    return get_audio_length(output_path)