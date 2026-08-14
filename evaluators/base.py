from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel


class EvalResult(BaseModel):
    score: float
    passed: bool
    metadata: Dict[str, Any] = {}
    reasoning: str = ""


class BaseEvaluator(ABC):
    name: str = "base"

    @abstractmethod
    def evaluate(self, prediction: str, reference: str, **kwargs) -> EvalResult:
        pass

    async def aevaluate(self, prediction: str, reference: str, **kwargs) -> EvalResult:
        return self.evaluate(prediction, reference, **kwargs)
