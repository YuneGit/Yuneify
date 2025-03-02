from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
from openai import OpenAI
import os
import openai
from pydantic import BaseModel, validator
import reapy

class AIModelError(Exception):
    """Base exception for AI model errors"""
    pass

class BaseAIModel(ABC):
    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str, midi_data: Dict, **kwargs) -> str:
        """Generate text response from AI model.
        
        Args:
            system_prompt: Role definition for the AI
            user_prompt: User instructions/query
            midi_data: Dictionary containing MIDI information
            kwargs: Additional model-specific parameters
            
        Returns:
            str: Generated text response
        """
        pass

class OpenAIModel(BaseAIModel):
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.client = OpenAI(timeout=30)
        self.model_name = model_name

    def generate_text(self, system_prompt: str, user_prompt: str, midi_data: Dict, **kwargs) -> str:
        try:
            midi_str = json.dumps(midi_data, indent=2)
            # Remove response_format from kwargs if present to prevent duplication
            kwargs.pop('response_format', None)
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},  # Correct single usage
                messages=[
                    {"role": "system", "content": f"{system_prompt}\nAlways respond with valid JSON"},
                    {"role": "user", "content": f"{user_prompt}\n```json\n{midi_str}\n```"},
                ],
                timeout=30,
                **kwargs
            )
            response = completion.choices[0].message.content.strip()
            
            if not response:
                raise AIModelError("Empty response from AI model")

            # Detailed JSON validation with position tracking
            try:
                json.loads(response)
            except json.JSONDecodeError as e:
                error_context = response[max(0, e.pos-50):e.pos+50]
                error_msg = (
                    f"JSON Parse Error: {e.msg}\n"
                    f"At position: {e.pos} (line {e.lineno}, column {e.colno})\n"
                    f"Context: ...{error_context}...\n"
                    f"Full response start: {response[:200]}"  # Show beginning of response
                )
                raise AIModelError(error_msg)
                
            return response
        except openai.APITimeoutError:
            raise AIModelError("API request timed out. Please try again.")
        except openai.APIConnectionError:
            raise AIModelError("Network connection failed. Check your internet.")
        except Exception as e:
            error_info = f"""
            === ERROR DETAILS ===
            System Prompt: {system_prompt}
            User Prompt: {user_prompt}
            MIDI Data: {midi_str[:500]}...
            Error: {str(e)}
            """
            print(error_info)  # Or log to file
            raise

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

MODEL_CONFIG = {
    'openai': {
        'class': OpenAIModel,
        'defaults': {'temperature': 0.7, 'max_tokens': 2000}
    },
    'gemma': {
        'class': GoogleGemmaModel,
        'defaults': {'temperature': 0.5, 'max_tokens': 4000}
    }
}

def get_model_handler(model_name: str) -> BaseAIModel:
    """Get configured model handler with defaults."""
    config = MODEL_CONFIG.get(model_name.lower())
    if not config:
        raise ValueError(f"Unsupported model: {model_name}")
    
    model = config['class']()
    model.default_params = config['defaults']
    return model

class MidiNote(BaseModel):
    start: float
    end: float 
    pitch: int
    velocity: int
    channel: int
    selected: bool
    muted: bool

class OrchestrationPlan(BaseModel):
    instruments: Dict[int, str]
    notes: List[Dict[str, Any]]
    dynamics: Dict[int, str] = {}
    articulation: str = "default"

    @validator('dynamics', pre=True)
    def convert_dynamics_keys(cls, v):
        """Convert dynamics keys to integers safely"""
        converted = {}
        for key, value in v.items():
            try:
                converted[int(key)] = value
            except (ValueError, TypeError):
                continue
        return converted

    @validator('notes', each_item=True)
    def validate_notes(cls, v):
        required = ['start', 'end', 'pitch', 'velocity']
        if not all(key in v for key in required):
            raise ValueError(f"Note missing required fields: {v}")
        v.setdefault('channel', 1)
        return v

def validate_midi_item(item: reapy.Item) -> reapy.Take:
    """Validate and return active take from MIDI item."""
    if not item:
        raise ValueError("No MIDI item selected")
    take = item.active_take
    if not take:
        raise ValueError("No active take")
    if not take.notes:
        raise ValueError("No MIDI notes found")
    return take
