import json
from typing import Optional
from pydantic import BaseModel
from evaluators.base import BaseEvaluator, EvalResult
from target.providers import GeminiTarget
from google.genai import types


class JudgeSchema(BaseModel):
    score: float
    passed: bool
    reasoning: str


class LLMJudgeEvaluator(BaseEvaluator):
    name = "llm_judge"

    def __init__(self, judge_target: GeminiTarget, threshold: float = 0.7):
        self.judge = judge_target
        self.threshold = threshold

    def evaluate(self, prediction: str, reference: str, **kwargs) -> EvalResult:
        raise NotImplementedError(
        "LLMJudgeEvaluator is async-only — call aevaluate() instead."
    )

    async def aevaluate(self, prediction: str, reference: str, **kwargs) -> EvalResult:
        question = kwargs.get("question", "")

        prompt = f"""You are evaluating a RAG (Retrieval-Augmented Generation) system.

Question: {question}
Reference Answer: {reference}
Model Response: {prediction}

Evaluate the model response on:
1. Accuracy (0.6): Is the factual content correct relative to the reference?
2. Completeness (0.3): Are all key points from the reference present?
3. Clarity (0.1): Is the response well-structured and easy to understand?

Return a JSON object with:
- score: float between 0.0 and 1.0
- passed: boolean (true if score >= {self.threshold})
- reasoning: one-sentence explanation
"""

        try:
            response = await self.judge.generate(
                prompt=prompt,
                system_prompt="You are a fair, rigorous evaluator. Always respond with valid JSON.",
                response_mime_type="application/json",
                response_schema=JudgeSchema,
            )

            data = json.loads(response.text)
            score = float(data.get("score", 0.0))
            passed = score >= self.threshold
            reasoning = data.get("reasoning", "")

        except Exception as e:
            score = 0.0
            passed = False
            reasoning = f"Judge parse error: {e}"

        return EvalResult(score=score, passed=passed, reasoning=reasoning)
