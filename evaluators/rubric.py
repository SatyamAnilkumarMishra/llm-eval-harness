from typing import List, Dict, Any, Callable
from evaluators.base import BaseEvaluator, EvalResult


class RubricEvaluator(BaseEvaluator):
    name = "rubric"

    def __init__(self, criteria: List[Dict[str, Any]], threshold: float = 0.8):
        """
        criteria: list of dicts like
            {"name": "has_substance", "weight": 1.0, "check": lambda p, r: ...}
        threshold: minimum weighted score (0.0-1.0) to count as passed.
        """
        self.criteria = criteria
        self.threshold = threshold

    def evaluate(self, prediction: str, reference: str, **kwargs) -> EvalResult:
        total_score = 0.0
        total_weight = 0.0
        details = []

        for crit in self.criteria:
            name = crit["name"]
            weight = crit.get("weight", 1.0)
            check: Callable[[str, str], bool] = crit["check"]

            passed = check(prediction, reference)
            score = 1.0 if passed else 0.0
            total_score += score * weight
            total_weight += weight
            details.append(f"{name}: {score} (weight {weight})")

        final_score = total_score / total_weight if total_weight > 0 else 0.0

        return EvalResult(
            score=final_score,
            passed=final_score >= self.threshold,
            reasoning="; ".join(details),
        )
