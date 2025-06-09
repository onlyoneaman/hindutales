from enum import Enum

class GptImageDimensions(str, Enum):
    PORTRAIT = "1024x1536"
    LANDSCAPE = "1536x1024"
    SQUARE = "1024x1024"

class GptImageQualities(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class GoogleImageAspectRatios(str, Enum):
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    SQUARE = "1:1"