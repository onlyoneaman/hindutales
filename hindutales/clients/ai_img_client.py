import base64
import time
import os
from google.genai.types import GenerateImagesConfig

from hindutales.clients.gemini_client import genai_client
from hindutales.clients.openai_client import openai_client
from hindutales.constants.constants import GptImageDimensions, GptImageQualities, GoogleImageAspectRatios
from hindutales.constants.models import AiProviders, LatestModels, GoogleImageModels
from hindutales.utils.fs_utils import save_to_file, sanitize_filename

class AIImgClient:
    def __init__(self):
        pass

    def generate_image_from_text(self, text: str, provider: AiProviders = AiProviders.GOOGLE) -> bytes:
        if provider == AiProviders.OPENAI:
            return self.generate_image_from_text_openai(text)
        elif provider == AiProviders.GOOGLE:
            return self.generate_image_from_text_google(text)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate_image_from_text_openai(self, text: str) -> bytes:
        result = openai_client.images.generate(
            model=LatestModels.openai_image,
            prompt=text,
            size=GptImageDimensions.PORTRAIT,
            quality=GptImageQualities.LOW,
        )
        image_base64: str = result.data[0].b64_json
        image_bytes: bytes = base64.b64decode(image_base64)
        return image_bytes

    def generate_image_from_text_google(self, text: str) -> bytes:
        try:
            response = genai_client.models.generate_images(
                model=GoogleImageModels.IMAGEN_3_0_GENERATE_002,
                prompt=text,
                config=GenerateImagesConfig(
                    number_of_images= 1,
                    aspect_ratio=GoogleImageAspectRatios.PORTRAIT
                )
            )
            generated_image = response.generated_images[0]
            image_bytes = generated_image.image.image_bytes
            return image_bytes
        except Exception as e:
            print(f"Error generating image: {e}")
            raise Exception("Failed to generate image")

if __name__ == "__main__":
    ai_img_client = AIImgClient()
    prompt = "A close-up of Abhimanyu battling ferociously within the Chakravyuh formation. He grips his sword with one hand and shields himself with the other, his golden armor glowing faintly against the darkened, smoky battlefield. His expression is fierce yet focused, sweat glistening on his forehead. Around him, enemy warriors are encroaching, their weapons gleaming ominously. The scene captures the intensity of the fight and the strategic complexity of the formation."
    output_path = "tmp/imgs"
    os.makedirs(output_path, exist_ok=True)
    filename = f"{int(time.time())}_{sanitize_filename(prompt)}.jpg"
    full_path = os.path.join(output_path, filename)
    image_bytes = ai_img_client.generate_image_from_text(prompt, provider=AiProviders.GOOGLE)
    save_to_file(image_bytes, full_path)
    print(f"Generated image saved to: {full_path}")
    