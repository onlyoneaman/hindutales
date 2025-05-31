from typing import List

class ImageMaker:
    def __init__(self):
        pass
    
    @staticmethod
    def generate(prompts: List[str]) -> List[str]:
        """
        Given a list of prompts, generate images for each prompt.
        """
        images_list: list = []
        for prompt in prompts:
            placeholder_image = "https://via.placeholder.com/150"
            images_list.append(placeholder_image)        
        return images_list
