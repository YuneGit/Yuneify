from abc import ABC, abstractmethod
from typing import Dict, Any
import json
from openai import OpenAI
import os

class AIModelError(Exception):
    """Base exception for AI model errors"""
    pass

class BaseAIModel(ABC):
    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str, midi_data: Dict, **kwargs) -> str:
        pass

class OpenAIModel(BaseAIModel):
    def __init__(self, model_name: str = "gpt-4"):
        self.client = OpenAI(timeout=10)
        self.model_name = model_name

    def generate_text(self, system_prompt: str, user_prompt: str, midi_data: Dict, **kwargs) -> str:
        try:
            midi_str = json.dumps(midi_data, indent=2)
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{user_prompt}\n```json\n{midi_str}\n```"},
                ],
                **kwargs
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise AIModelError(f"OpenAI API error: {str(e)}")

class GoogleGemmaModel(BaseAIModel):
    def __init__(self, model_name: str = "gemma-7b"):
        # Implementation would require Google Cloud setup
        self.model_name = model_name

    def generate_text(self, system_prompt: str, user_prompt: str, midi_data: Dict, **kwargs) -> str:
        raise NotImplementedError("Gemma integration not yet implemented")

class DeepSeekModel(BaseAIModel):
    def __init__(self, model_name: str = "deepseek-music"):
        # Implementation would require DeepSeek API setup
        self.model_name = model_name

    def generate_text(self, system_prompt: str, user_prompt: str, midi_data: Dict, **kwargs) -> str:
        raise NotImplementedError("DeepSeek integration not yet implemented")

def get_model_handler(model_name: str) -> BaseAIModel:
    model_config = {
        "openai": OpenAIModel,
        "gemma": GoogleGemmaModel,
        "deepseek": DeepSeekModel
    }
    
    if model_name not in model_config:
        raise ValueError(f"Unsupported model: {model_name}")
        
    return model_config[model_name]()
