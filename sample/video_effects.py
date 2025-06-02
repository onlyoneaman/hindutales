import ffmpeg

def printVideoAspectRatio(filePath: str) -> None:
    """Prints the aspect ratio of the given video file using ffmpeg-python."""
    probe: dict = ffmpeg.probe(filePath)
    videoStreams: list[dict] = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if not videoStreams:
        print("No video stream found.")
        return
    width: int = int(videoStreams[0]['width'])
    height: int = int(videoStreams[0]['height'])
    aspectRatio: float = width / height
    print(f"Aspect Ratio: {aspectRatio:.6f} ({width}:{height})")


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

if __name__ == "__main__":
    inputPath: str = "sample/King Shibi’s Test.mp4"
    outputPath: str = "sample/King Shibi’s Test_resized.mp4"
    printVideoAspectRatio(inputPath)
    resizeIfSquareVideo(inputPath, outputPath)
