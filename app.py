from dotenv import load_dotenv
from hindutales.core.video_maker import VideoMaker, VideoMakerParams
import time

def main():
    load_dotenv()
    start_time = time.time()
    title = "Curse of Ahalya"
    video_maker = VideoMaker(params=VideoMakerParams(title=title, lang="gujarati"))
    result = video_maker.generate()
    print("5. Saving video")
    video_maker.save_video(result, title)
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time}")
    print(result)
    
if __name__ == "__main__":
    main()
    