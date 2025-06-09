from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Type, TypeVar, Union, List
from hindutales.clients.gemini_client import client
import json

T = TypeVar("T", bound=BaseModel)

load_dotenv()

class T2TConverter:
    def __init__(self, model: str = 'gemini-2.0-flash-lite', temperature: float = 0.7, top_p: float = 0.9) -> None:
        """
        Initialize the T2TConverter with AzureOpenAI parameters.

        :param model: The model name to use for AzureOpenAI.
        :param temperature: Sampling temperature for the model.
        :param top_p: Nucleus sampling parameter.
        """
        self.model = model
        self.temperature = temperature
        self.top_p = top_p

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        output_type: Union[Type[T], Type[List[T]]],
        input_data: Union[BaseModel, List[BaseModel], None] = None,
    ) -> Union[T, List[T]]:
        """
        Convert input data to the desired output type using AzureOpenAI.

        :param input_data: A Pydantic object or list of Pydantic objects.
        :param system_prompt: The system prompt to guide the model's behavior.
        :param user_prompt: The user prompt to provide context for the conversion.
        :param output_type: The desired output type (Pydantic model or list of Pydantic models).
        :return: The converted output in the specified format.
        """
        if input_data is not None:
            if isinstance(input_data, BaseModel):
                input_json = input_data.model_dump_json()
            elif isinstance(input_data, list) and all(isinstance(item, BaseModel) for item in input_data):
                input_json = json.dumps([item.model_dump_json() for item in input_data])
            else:
                raise ValueError("Input data must be a Pydantic object or a list of Pydantic objects.")
        else:
            input_json = None

        if input_json is not None:
            user_msg = f"{user_prompt}\nInput: {input_json}"
        else:
            user_msg = user_prompt
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
        response = None
        try:
            response = client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                top_p=self.top_p,
                response_format=output_type,
            )
            content = response.choices[0].message.content

            if isinstance(content, dict):
                parsed = content
            else:
                parsed = json.loads(content)
            if issubclass(output_type, BaseModel):
                return output_type(**parsed)
            elif issubclass(output_type, list) and all(issubclass(output_type.__args__[0], BaseModel) for _ in output_type.__args__):
                return [output_type.__args__[0](**item) for item in parsed]
            else:
                raise ValueError("Output type must be a Pydantic model or a list of Pydantic models.")
        except Exception as e:
            if response:
                raise ValueError(f"Failed to process AzureOpenAI output: {e}\nRaw output: {getattr(response.choices[0].message, 'content', '')}")
            raise ValueError(f"Failed to process AzureOpenAI output: {e}")
        
