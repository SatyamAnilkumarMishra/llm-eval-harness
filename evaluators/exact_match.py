from evaluators.base import BaseEvaluator, EvalResult


class ExactMatchEvaluator(BaseEvaluator):
    name = "exact_match"

    def __init__(self, case_sensitive: bool = False, strip: bool = True):
        self.case_sensitive = case_sensitive
        self.strip = strip

    def evaluate(self, prediction: str, reference: str, **kwargs) -> EvalResult:
        pred = prediction.strip() if self.strip else prediction
        ref = reference.strip() if self.strip else reference

        if not self.case_sensitive:
            pred = pred.lower()
            ref = ref.lower()

        passed = pred == ref
        return EvalResult(
            score=1.0 if passed else 0.0,
            passed=passed,
            reasoning="Exact match" if passed else f"Expected '{ref}', got '{pred}'",
        )
