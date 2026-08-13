from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel


class TargetResponse(BaseModel):
  
    text: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0
    raw: Optional[Dict[str, Any]] = None


class BaseTarget(ABC):
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs

    @abstractmethod
    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **generation_kwargs
    ) -> TargetResponse:
        pass
