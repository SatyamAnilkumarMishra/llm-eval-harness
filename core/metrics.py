from typing import List, Dict, Any
from statistics import mean


class MetricsTracker:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def add(self, result: Dict[str, Any]):
        self.results.append(result)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r["passed"]) / len(self.results)

    @property
    def avg_score(self) -> float:
        if not self.results:
            return 0.0
        return mean(r["score"] for r in self.results)

    @property
    def avg_latency_ms(self) -> float:
        if not self.results:
            return 0.0
        return mean(r["latency_ms"] for r in self.results)

    @property
    def total_tokens(self) -> Dict[str, int]:
        prompt = 0
        completion = 0
        for r in self.results:
            usage = r.get("usage") or {}
            if usage and isinstance(usage, dict):
                pt = usage.get("prompt_tokens")
                ct = usage.get("completion_tokens")
                if pt is not None:
                    prompt += pt
                if ct is not None:
                    completion += ct
        return {"prompt": prompt, "completion": completion}

    def summary(self) -> Dict[str, Any]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        return {
            "total_samples": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": self.pass_rate,
            "avg_score": self.avg_score,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "total_tokens": self.total_tokens,
        }
