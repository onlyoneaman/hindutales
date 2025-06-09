from enum import Enum

class AutoValueClass:
    def __init_subclass__(cls):
        for key, val in cls.__dict__.items():
            if isinstance(val, Enum):
                setattr(cls, key, val.value)

class AiProviders(AutoValueClass):
    GOOGLE = "google"
    OPENAI = "openai"

class GeminiModels(AutoValueClass):
    GEMINI_2_5_FLASH_PREVIEW_05_20 = "gemini-2.5-flash-preview-05-20"
    GEMINI_2_5_PRO_PREVIEW_06_05 = "gemini-2.5-pro-preview-06-05"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"

class GoogleImageModels(AutoValueClass):
    IMAGEN_3_0_GENERATE_002 = "imagen-3.0-generate-002"
    IMAGEN_3_0_FAST_GENERATE_001 = "imagen-3.0-fast-generate-001"

class OpenAIImageModels(AutoValueClass):
    GPT_IMAGE_1 = "gpt-image-1"

class LatestModels(AutoValueClass):
    gemini_high = GeminiModels.GEMINI_2_5_FLASH_PREVIEW_05_20
    gemini_pro = GeminiModels.GEMINI_2_5_PRO_PREVIEW_06_05
    gemini_mid = GeminiModels.GEMINI_2_0_FLASH
    gemini_lite = GeminiModels.GEMINI_2_0_FLASH_LITE
    openai_image = OpenAIImageModels.GPT_IMAGE_1
