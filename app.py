from dotenv import load_dotenv
from hindutales.core.video_maker import VideoMaker, VideoMakerParams
import time

def main():
    load_dotenv()
    start_time = time.time()
    title = "The Clever Weaver (Rajasthan) - A poor weaver promises a magical turban to a greedy king, but cleverly uses wit to expose the king’s greed and injustice."
    video_maker = VideoMaker(params=VideoMakerParams(title=title, lang="english"))
    result = video_maker.generate()
    print("5. Saving video")
    video_maker.save_video(result, title)
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time}")
    print(result)
    
if __name__ == "__main__":
    main()
    