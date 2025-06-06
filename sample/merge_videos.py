import ffmpeg
import os
import time
from typing import Literal

def merge_videos(video_paths: list[str], output_path: str, 
                transition: Literal['fade', 'slide', 'simple'] = 'fade', 
                transition_duration: float = 1.0) -> None:
    """
    Merge multiple videos with specified transition effect between each pair.
    
    Args:
        video_paths: List of paths to video files to merge
        output_path: Path for merged output video
        transition: Type of transition ('fade', 'slide', 'simple')
        transition_duration: Duration of transition in seconds (ignored for 'simple')
    """
    
    if len(video_paths) < 2:
        print("Need at least 2 videos to merge.")
        return
    
    # Check if input files exist
    for file_path in video_paths:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return
    
    print(f"Merging {len(video_paths)} videos with {transition} transition...")
    
    # Load all video inputs
    videos = [ffmpeg.input(path) for path in video_paths]
    
    if transition == 'simple':
        # Simple concatenation without transitions
        video_streams = [video['v'] for video in videos]
        audio_streams = [video['a'] for video in videos]
        
        # Concatenate all video and audio streams
        video_concat = ffmpeg.concat(*video_streams, v=1, a=0)
        audio_concat = ffmpeg.concat(*audio_streams, v=0, a=1)
        
        # Create output with both streams
        output = ffmpeg.output(video_concat, audio_concat, output_path,
                              vcodec='libx264', acodec='aac')
    else:
        # Build transitions sequentially
        current_video = videos[0]['v']
        current_audio = videos[0]['a']
        current_duration = 0
        
        for i in range(1, len(videos)):
            # Get duration of current video for transition timing
            prev_video_duration = float(ffmpeg.probe(video_paths[i-1])['format']['duration'])
            current_duration += prev_video_duration
            
            next_video = videos[i]['v']
            next_audio = videos[i]['a']
            
            # Create video transition
            if transition == 'fade':
                current_video = ffmpeg.filter([current_video, next_video], 'xfade',
                                            transition='fade',
                                            duration=transition_duration,
                                            offset=current_duration - transition_duration)
            elif transition == 'slide':
                current_video = ffmpeg.filter([current_video, next_video], 'xfade',
                                            transition='slideleft',
                                            duration=transition_duration,
                                            offset=current_duration - transition_duration)
            
            # Concatenate audio streams (no crossfade to avoid overlap)
            current_audio = ffmpeg.concat(current_audio, next_audio, v=0, a=1)
        
        # Create output
        output = ffmpeg.output(
            current_video,
            current_audio,
            output_path,
            vcodec='libx264',
            acodec='aac',
            preset='medium',
            crf=23,
        )
    
    ffmpeg.run(output, quiet=True, overwrite_output=True)
    print(f"Merged video saved as {output_path}")

if __name__ == "__main__":
    video1_path = "sample/Bhishma's Vow_padded.mp4"
    video2_path = "sample/Ganga’s Silent Sacrifice_padded.mp4"
    video3_path = "sample/Prahlad and Hiranyakashipu_resized_padded.mp4"
    output_path = "sample/merged_stories.mp4"
    
    time_start = time.time()
    
    # Slide transition (default example)
    # merge_videos(video1_path, video2_path, output_path, transition='slide', transition_duration=2.0)
    
    # Other options:
    # List of videos to merge
    video_paths = [video1_path, video2_path, video3_path]
    
    # Examples of different merge options:
    merge_videos(video_paths, output_path, transition='simple', transition_duration=1.5)
    # merge_videos(video1_path, video2_path, output_path, transition='simple')

    end_time = time.time()
    print(f"Time taken: {end_time - time_start}")
