from typing import List, Tuple
import ffmpeg

def create_audio_image_pairs(audio_files: List[str], image_files: List[str]) -> List[Tuple[str, str, float]]:
    """
    Smart pairing of audio and image files regardless of count differences.
    Returns list of (audio_file, image_file, segment_duration) tuples.
    """
    audio_count = len(audio_files)
    image_count = len(image_files)
    
    print(f"Matching strategy: {audio_count} audio files → {image_count} image files")
    
    # Get total audio duration
    total_audio_duration = 0
    audio_durations = []
    for audio_file in audio_files:
        probe = ffmpeg.probe(audio_file)
        duration = float(probe['format']['duration'])
        audio_durations.append(duration)
        total_audio_duration += duration
    
    pairs = []
    
    if audio_count == image_count:
        # 1:1 mapping - simple case
        print("Using 1:1 audio-image mapping")
        for audio, image, duration in zip(audio_files, image_files, audio_durations):
            pairs.append((audio, image, duration))
    
    elif audio_count > image_count:
        # More audio than images - multiple audios per image
        audios_per_image = audio_count // image_count
        remaining_audios = audio_count % image_count
        
        print(f"Using {audios_per_image}+ audios per image strategy")
        
        audio_idx = 0
        for img_idx, image in enumerate(image_files):
            # Calculate how many audios this image should get
            audios_for_this_image = audios_per_image
            if img_idx < remaining_audios:
                audios_for_this_image += 1
            
            # Combine multiple audios for this image
            combined_duration = sum(audio_durations[audio_idx:audio_idx + audios_for_this_image])
            
            # Create one segment per audio, but using the same image
            for i in range(audios_for_this_image):
                pairs.append((audio_files[audio_idx + i], image, audio_durations[audio_idx + i]))
            
            audio_idx += audios_for_this_image
    
    else:
        # More images than audios - multiple images per audio
        images_per_audio = image_count // audio_count
        remaining_images = image_count % audio_count
        
        print(f"Using {images_per_audio}+ images per audio strategy")
        
        image_idx = 0
        for aud_idx, (audio, duration) in enumerate(zip(audio_files, audio_durations)):
            # Calculate how many images this audio should get
            images_for_this_audio = images_per_audio
            if aud_idx < remaining_images:
                images_for_this_audio += 1
            
            # Split audio duration equally among images
            segment_duration = duration / images_for_this_audio
            
            # Create segments for each image using portion of this audio
            for i in range(images_for_this_audio):
                # For multiple images per audio, we'll need to create audio segments
                start_time = i * segment_duration
                pairs.append((audio, image_files[image_idx + i], segment_duration, start_time))
            
            image_idx += images_for_this_audio
    
    print(f"Created {len(pairs)} video segments")
    return pairs

def create_audio_segment(input_audio: str, output_path: str, start_time: float, duration: float):
    """Create a segment of audio file"""
    (
        ffmpeg
        .input(input_audio, ss=start_time, t=duration)
        .output(output_path, acodec='copy')
        .run(overwrite_output=True, quiet=True)
    )

