from typing import List
from dotenv import load_dotenv
import base64
from hindutales.client.openai_client import client
import uuid
import os

load_dotenv()

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
            placeholder_image = ImageMaker.generate_image(prompt)
            images_list.append(placeholder_image)        
        return images_list

    @staticmethod
    def generate_image(prompt: str) -> bytes:
        """
        Given a prompt, generate an image.
        """
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="medium",
        )
        image_base64: str = result.data[0].b64_json
        image_bytes: bytes = base64.b64decode(image_base64)
        uniq_id = uuid.uuid4()
        img_folder_name = "images"
        os.makedirs(img_folder_name, exist_ok=True)
        with open(f"{img_folder_name}/{uniq_id}.png", "wb") as f:
            f.write(image_bytes)
        return uniq_id