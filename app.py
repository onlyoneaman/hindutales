from dotenv import load_dotenv
from hindutales.core.video_maker import VideoMaker, VideoMakerParams
import time

def main():
    load_dotenv()
    start_time = time.time()
    title = "Bhishma's Vow"
    description = "To end his father’s sorrow, Bhishma renounced the throne—and love—forever. In a moment that altered the fate of the Kuru dynasty, he swore a lifelong vow of celibacy so that Satyavati’s children could rule. The gods watched in awe, naming him Bhishma—the one of the terrible vow. A tale of duty, sacrifice, and unshakable resolve."
    params = VideoMakerParams(title=title, lang="english", description=description)
    video_maker = VideoMaker(params=params)
    result = video_maker.generate()
    print("5. Saving video")
    video_maker.save_video(result, title)
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time}")
    print(result)
    
if __name__ == "__main__":
    main()
    