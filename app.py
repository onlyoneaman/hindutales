from hindutales.core.video_maker import VideoMaker, VideoMakerParams
import time

def main():
    start_time = time.time()
    video_maker = VideoMaker(params=VideoMakerParams(title="Sita’s Agni Pariksha"))
    result = video_maker.generate()
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time}")
    print(result)
    
if __name__ == "__main__":
    main()
    