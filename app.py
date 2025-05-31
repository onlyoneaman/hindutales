from hindutales.core.video_maker import VideoMaker, VideoMakerParams

def main():
    video_maker = VideoMaker(params=VideoMakerParams(title="Ganesha Tooth"))
    result = video_maker.generate()
    print(result)
    
if __name__ == "__main__":
    main()
    