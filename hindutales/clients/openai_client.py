from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

azure_client = AzureOpenAI(
    api_version="2024-02-01",
    api_key=os.getenv("AZURE_OPENAI_API_KEY_2"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT_2"),
)
