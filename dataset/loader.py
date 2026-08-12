import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvalSample(BaseModel):
    id: str
    context: Optional[str] = None
    question: str
    expected_answer: str
    evaluator: str = "exact_match"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetLoader:
    @staticmethod
    def from_json(path: str) -> List[EvalSample]:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, dict) and "samples" in raw:
            raw = raw["samples"]
        return [EvalSample(**item) for item in raw]

    @staticmethod
    def from_jsonl(path: str) -> List[EvalSample]:

        samples = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    samples.append(EvalSample(**json.loads(line)))
        return samples