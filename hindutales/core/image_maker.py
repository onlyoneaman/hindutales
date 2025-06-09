from dotenv import load_dotenv
import base64
from hindutales.clients.openai_client import client, azure_client
import uuid
import os
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAIError
import time
import requests

load_dotenv()

DIMENSIONS = "1024x1536"

class ImageMaker:
    def __init__(self):
        pass
    
    @staticmethod
    def generate(prompts: list[str]) -> list[bytes]:
        """
        Given a list of prompts, generate images for each prompt in parallel.
        """
        images_list: list[bytes] = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(ImageMaker.generate_image, prompt,retries=3,backoff=61) for prompt in prompts]
            for future in futures:
                images_list.append(future.result())
        return images_list

    @staticmethod
    def generate_image(prompt: str, retries: int = 3, backoff: int = 1) -> bytes:
        """
        Given a prompt, generate an image.
        """
        for attempt in range(retries):
            try:
                result = client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=DIMENSIONS,
                    quality="high",
                )
                image_base64: str = result.data[0].b64_json
                image_bytes: bytes = base64.b64decode(image_base64)
                break
            except OpenAIError as e:
                if attempt < retries - 1:
                    time.sleep(backoff * (2 ** attempt))
                else:
                    result = azure_client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size=DIMENSIONS,
                        n=1,
                        style="vivid",
                        quality="standard",
                        moderation="low",
                    )
                    url = result.data[0].url
                    image_bytes = requests.get(url).content
        uniq_id = uuid.uuid4()
        img_folder_name = "images"
        os.makedirs(img_folder_name, exist_ok=True)
        with open(f"{img_folder_name}/{uniq_id}.png", "wb") as f:
            f.write(image_bytes)
        return uniq_id

    @staticmethod
    def generate_image_dall_e(prompt: str, retries: int = 3, backoff: int = 1) -> bytes:
        """
        Given a prompt, generate an image using DALL-E.
        """
        for attempt in range(retries):
            try:
                break
            except OpenAIError as e:
                if attempt < retries - 1:
                    time.sleep(backoff * (2 ** attempt))
                else:
                    raise e
        image_base64: str = result.data[0].b64_json
        image_bytes: bytes = base64.b64decode(image_base64)
        uniq_id = uuid.uuid4()
        img_folder_name = "images"
        os.makedirs(img_folder_name, exist_ok=True)
        with open(f"{img_folder_name}/{uniq_id}.png", "wb") as f:
            f.write(image_bytes)
        return uniq_id
