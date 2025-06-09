from typing import List, Dict, Optional
import json
import logging

from hindutales.clients.gemini_client import client
from hindutales.constants.models import LatestModels

logger = logging.getLogger(__name__)

def get_llm_response(
    messages: List[Dict[str, str]], 
    model: str = LatestModels.gemini_lite,
    response_format: object = None,
    temperature: float = 0.8,
    top_p: float = 0.9,
    allow_fallback: bool = False
):
    fallback_models = []
    if allow_fallback:
        if model != LatestModels.gemini_mid:
            fallback_models.append(LatestModels.gemini_mid)
        if model != LatestModels.gemini_high and LatestModels.gemini_high != fallback_models[-1] if fallback_models else False:
            fallback_models.append(LatestModels.gemini_high)
    
    last_exception: Optional[Exception] = None
    models_to_try = [model] + fallback_models
    
    for current_model in models_to_try:
        try:
            logger.debug(f"Attempting with model: {current_model}")
            resp = client.beta.chat.completions.parse(
                model=current_model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                response_format=response_format
            )
            content = resp.choices[0].message.content
            if isinstance(content, dict):
                parsed = content
            else:
                parsed = json.loads(content)
            return response_format(**parsed)
        except Exception as e:
            last_exception = e
            logger.warning(f"Failed with model {current_model}: {str(e)}")
            continue
    
    # If we get here, all models have failed
    raw_output = ""
    if last_exception and hasattr(last_exception, "response") and hasattr(last_exception.response, "choices"):
        raw_output = getattr(last_exception.response.choices[0].message, "content", "")
    
    raise ValueError(f"Failed to get response from all models ({', '.join(models_to_try)}): {str(last_exception)}\nRaw output: {raw_output}")