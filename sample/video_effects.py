import ffmpeg
import os

def printVideoAspectRatio(filePath: str) -> None:
    """Prints the aspect ratio of the given video file using ffmpeg-python."""
    # check file exists
    if not os.path.exists(filePath):
        print(f"File {filePath} does not exist.")
        return
    probe: dict = ffmpeg.probe(filePath)
    videoStreams: list[dict] = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if not videoStreams:
        print("No video stream found.")
        return
    width: int = int(videoStreams[0]['width'])
    height: int = int(videoStreams[0]['height'])
    aspectRatio: float = width / height
    print(f"Aspect Ratio: {aspectRatio:.2f} ({width}:{height})")


def resizeIfSquareVideo(inputPath: str, outputPath: str) -> None:
    """If the video is 1:1 aspect ratio, resize it to 1024x1536 and save to outputPath."""
    probe: dict = ffmpeg.probe(inputPath)
    videoStreams: list[dict] = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if not videoStreams:
        print("No video stream found.")
        return
    width: int = int(videoStreams[0]['width'])
    height: int = int(videoStreams[0]['height'])
    if width == height:
        print(f"Square video detected ({width}x{height}). Resizing to 1024x1536...")
        (
            ffmpeg
            .input(inputPath)
            .filter('scale', 1024, 1536)
            .output(
                outputPath,
                vcodec='libx264',
                acodec='aac',
                strict='experimental',
                **{'map': '0:v', 'map': '0:a?'}
            )
            .overwrite_output()
            .run()
        )
        print(f"Resized video saved as {outputPath} (with audio if present)")
    else:
        print(f"Video is not square ({width}x{height}). No resizing performed.")

# given a file video could be square or rectangle, add space on top and bottom to make it 1080X1920
def addSpaceToVideo(inputPath: str, outputPath: str) -> None:
    probe: dict = ffmpeg.probe(inputPath)
    videoStreams: list[dict] = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if not videoStreams:
        print("No video stream found.")
        return
    width: int = int(videoStreams[0]['width'])
    height: int = int(videoStreams[0]['height'])
    
    targetWidth: int = 1080
    targetHeight: int = 1920
    
    print(f"Original video dimensions: {width}x{height}")
    
    # Calculate scale to fit width to 1080 while maintaining aspect ratio
    scale: float = targetWidth / width
    scaledHeight: int = int(height * scale)
    
    print(f"Scaled dimensions: {targetWidth}x{scaledHeight}")
    
    if scaledHeight > targetHeight:
        # If scaled height exceeds target, we need to scale down further to fit height
        scale = targetHeight / height
        scaledWidth = int(width * scale)
        scaledHeight = targetHeight
        print(f"Adjusted dimensions to fit height: {scaledWidth}x{scaledHeight}")
        
        # Center horizontally with black bars on left and right
        padX = (targetWidth - scaledWidth) // 2
        padY = 0
    else:
        # Video fits within target height, add padding top and bottom
        scaledWidth = targetWidth
        padX = 0
        padY = (targetHeight - scaledHeight) // 2
    
    print(f"Padding: {padX}x{padY}")
    print(f"Final output will be: {targetWidth}x{targetHeight}")
    
    (
        ffmpeg
        .input(inputPath)
        .filter('scale', scaledWidth, scaledHeight)
        .filter('pad', targetWidth, targetHeight, padX, padY, color='black')
        .output(
            outputPath,
            vcodec='libx264',
            acodec='aac',
            strict='experimental',
            **{'map': '0:v', 'map': '0:a?'}
        )
        .overwrite_output()
        .run()
    )
    print(f"Video with padding saved as {outputPath}")
    

if __name__ == "__main__":
    inputPath: str = "sample/Prahlad and Hiranyakashipu_resized.mp4"
    outputPath: str = "sample/Prahlad and Hiranyakashipu_resized_padded.mp4"
    printVideoAspectRatio(inputPath)
    # resizeIfSquareVideo(inputPath, outputPath)
    addSpaceToVideo(inputPath, outputPath)
