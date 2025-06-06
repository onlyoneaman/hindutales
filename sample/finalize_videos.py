import ffmpeg
import os
import time
from typing import Literal

def standardize_video_dimensions(input_path: str, output_path: str, target_width: int = 1080, target_height: int = 1920) -> None:
    """
    Standardize video to target dimensions by scaling and padding with black bars if needed.
    
    Args:
        input_path: Path to input video
        output_path: Path for standardized output video
        target_width: Target width (default 1080)
        target_height: Target height (default 1920)
    """
    if not os.path.exists(input_path):
        print(f"File {input_path} does not exist.")
        return
        
    probe = ffmpeg.probe(input_path)
    video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if not video_streams:
        print("No video stream found.")
        return
        
    width = int(video_streams[0]['width'])
    height = int(video_streams[0]['height'])
    
    print(f"Original video dimensions: {width}x{height}")
    
    # Calculate scale to fit width to target while maintaining aspect ratio
    scale = target_width / width
    scaled_height = int(height * scale)
    
    print(f"Scaled dimensions: {target_width}x{scaled_height}")
    
    if scaled_height > target_height:
        # If scaled height exceeds target, scale down further to fit height
        scale = target_height / height
        scaled_width = int(width * scale)
        scaled_height = target_height
        print(f"Adjusted dimensions to fit height: {scaled_width}x{scaled_height}")
        
        # Center horizontally with black bars on left and right
        pad_x = (target_width - scaled_width) // 2
        pad_y = 0
    else:
        # Video fits within target height, add padding top and bottom
        scaled_width = target_width
        pad_x = 0
        pad_y = (target_height - scaled_height) // 2
    
    print(f"Padding: {pad_x}x{pad_y}")
    print(f"Final output will be: {target_width}x{target_height}")
    
    (
        ffmpeg
        .input(input_path)
        .filter('scale', scaled_width, scaled_height)
        .filter('pad', target_width, target_height, pad_x, pad_y, color='black')
        .output(
            output_path,
            vcodec='libx264',
            acodec='aac',
            strict='experimental',
            **{'map': '0:v', 'map': '0:a?'}
        )
        .overwrite_output()
        .run(quiet=True)
    )
    print(f"Standardized video saved as {output_path}")

def finalize_videos(video_paths: list[str], output_path: str, 
                   transition: Literal['fade', 'slide', 'simple'] = 'fade', 
                   transition_duration: float = 1.0,
                   target_width: int = 1080, 
                   target_height: int = 1920) -> None:
    """
    Finalize videos by standardizing dimensions and applying transitions.
    
    Args:
        video_paths: List of paths to video files to merge
        output_path: Path for final merged video
        transition: Type of transition ('fade', 'slide', 'simple')
        transition_duration: Duration of transition in seconds (ignored for 'simple')
        target_width: Target width for all videos (default 1080)
        target_height: Target height for all videos (default 1920)
    """
    
    if len(video_paths) < 2:
        print("Need at least 2 videos to merge.")
        return
    
    # Check if input files exist
    for file_path in video_paths:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return
    
    print(f"Finalizing {len(video_paths)} videos with {transition} transition...")
    
    # Step 1: Standardize all videos to target dimensions
    standardized_paths = []
    temp_dir = os.path.dirname(output_path)
    
    for i, video_path in enumerate(video_paths):
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        standardized_path = os.path.join(temp_dir, f"temp_standardized_{i}_{base_name}.mp4")
        
        print(f"Standardizing video {i+1}/{len(video_paths)}: {video_path}")
        standardize_video_dimensions(video_path, standardized_path, target_width, target_height)
        standardized_paths.append(standardized_path)
    
    # Step 2: Merge standardized videos with transitions
    print(f"Merging standardized videos with {transition} transition...")
    
    # Load all standardized video inputs
    videos = [ffmpeg.input(path) for path in standardized_paths]
    
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
            prev_video_duration = float(ffmpeg.probe(standardized_paths[i-1])['format']['duration'])
            
            # For the first transition, use full duration
            # For subsequent transitions, account for previous overlaps
            if i == 1:
                current_duration = prev_video_duration
            else:
                current_duration += prev_video_duration - transition_duration
            
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
    
    # Run the final merge
    ffmpeg.run(output, quiet=True, overwrite_output=True)
    
    # Clean up temporary standardized files
    print("Cleaning up temporary files...")
    for temp_path in standardized_paths:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    print(f"Final video saved as {output_path}")

if __name__ == "__main__":
    # Example usage with videos of different dimensions
    video_paths = [
        "sample/Bhishma's Vow.mp4",          # Original dimensions
        "sample/Ganga’s Silent Sacrifice.mp4", # Original dimensions  
        "sample/Ekalavya’s Thumb.mp4"        # Original dimensions
    ]
    
    output_path = "sample/finalized_stories.mp4"
    
    time_start = time.time()
    
    # Test with fade transition
    finalize_videos(
        video_paths, 
        output_path, 
        transition='fade', 
        transition_duration=1.5,
        target_width=1080,
        target_height=1920
    )
    
    end_time = time.time()
    print(f"Total time taken: {end_time - time_start:.2f} seconds")