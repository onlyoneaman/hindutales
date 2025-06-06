import ffmpeg
import os
import time
from typing import Literal

def merge_videos(video1_path: str, video2_path: str, output_path: str, 
                transition: Literal['fade', 'slide', 'simple'] = 'fade', 
                transition_duration: float = 1.0) -> None:
    """
    Merge two videos with specified transition effect.
    
    Args:
        video1_path: Path to first video
        video2_path: Path to second video  
        output_path: Path for merged output video
        transition: Type of transition ('fade', 'slide', 'simple')
        transition_duration: Duration of transition in seconds (ignored for 'simple')
    """
    
    # Check if input files exist
    for file_path in [video1_path, video2_path]:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return
    
    print(f"Merging {video1_path} and {video2_path} with {transition} transition...")
    
    video1 = ffmpeg.input(video1_path)
    video2 = ffmpeg.input(video2_path)
    
    if transition == 'simple':
        # Simple concatenation without transitions
        output = ffmpeg.concat(video1, video2, v=1, a=1).output(
            output_path, vcodec='libx264', acodec='aac'
        )
    else:
        # Get video duration for transition timing
        video1_duration = float(ffmpeg.probe(video1_path)['format']['duration'])
        
        # Get video and audio streams
        v1 = video1['v']
        a1 = video1['a']
        v2 = video2['v'] 
        a2 = video2['a']
        
        # Create video transition
        if transition == 'fade':
            video_transition = ffmpeg.filter([v1, v2], 'xfade',
                                           transition='fade',
                                           duration=transition_duration,
                                           offset=video1_duration - transition_duration)
        elif transition == 'slide':
            video_transition = ffmpeg.filter([v1, v2], 'xfade',
                                           transition='slideleft', 
                                           duration=transition_duration,
                                           offset=video1_duration - transition_duration)
        
        # Concatenate audio without crossfade to avoid overlap
        audio_transition = ffmpeg.concat(a1, a2, v=0, a=1)
        
        # Create output
        output = ffmpeg.output(video_transition, audio_transition, output_path,
                              vcodec='libx264', acodec='aac', preset='medium', crf=23)
    
    ffmpeg.run(output, overwrite_output=True)
    print(f"Merged video saved as {output_path}")

if __name__ == "__main__":
    video1_path = "sample/Bhishma's Vow_padded.mp4"
    video2_path = "sample/Ganga’s Silent Sacrifice_padded.mp4"
    output_path = "sample/merged_stories.mp4"
    
    time_start = time.time()
    
    # Slide transition (default example)
    merge_videos(video1_path, video2_path, output_path, transition='slide', transition_duration=2.0)

    end_time = time.time()
    print(f"Time taken: {end_time - time_start}")
    
    # Other options:
    # merge_videos(video1_path, video2_path, output_path, transition='fade', transition_duration=1.5)
    # merge_videos(video1_path, video2_path, output_path, transition='simple')