import asyncio
from typing import List, Dict, Any, Optional
from dataset.loader import EvalSample
from target.base import BaseTarget
from evaluators.base import BaseEvaluator
from core.metrics import MetricsTracker
from core.recorder import ResultRecorder


class EvaluationRunner:
    def __init__(self, target: BaseTarget, max_concurrent: int = 5):
        self.target = target
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.metrics = MetricsTracker()
        self.recorder = ResultRecorder()

    def _build_prompt(self, sample: EvalSample) -> str:
        """RAG-style prompt construction: context first, then question.
        This is deliberately simple/naive — a real RAG eval might need
        to test multiple prompt templates, which is exactly the kind of
        thing `--compare` mode exists for."""
        if sample.context:
            return (
                f"Use the following context to answer the question.\n\n"
                f"Context:\n{sample.context}\n\n"
                f"Question: {sample.question}\n\n"
                f"Answer:"
            )
        return f"Question: {sample.question}\n\nAnswer:"

    async def _run_single(
        self,
        sample: EvalSample,
        evaluators: Dict[str, BaseEvaluator],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        async with self.semaphore:
            prompt = self._build_prompt(sample)

            response = await self.target.generate(prompt, system_prompt)

            evaluator = evaluators.get(sample.evaluator)
            if evaluator is None:
                raise ValueError(
                    f"No evaluator registered for '{sample.evaluator}' "
                    f"(sample id: {sample.id})"
                )

            eval_result = await evaluator.aevaluate(
                prediction=response.text,
                reference=sample.expected_answer,
                question=sample.question,
                context=sample.context,
            )

            result = {
                "id": sample.id,
                "prompt": prompt,
                "prediction": response.text,
                "expected": sample.expected_answer,
                "evaluator": sample.evaluator,
                "score": eval_result.score,
                "passed": eval_result.passed,
                "reasoning": eval_result.reasoning,
                "latency_ms": response.latency_ms,
                "usage": response.usage,
                "metadata": sample.metadata,
            }

            self.metrics.add(result)
            self.recorder.save(result)
            return result

    async def run(
        self,
        dataset: List[EvalSample],
        evaluators: Dict[str, BaseEvaluator],
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        tasks = [
            self._run_single(s, evaluators, system_prompt) for s in dataset
        ]
        return await asyncio.gather(*tasks)
