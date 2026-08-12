import asyncio
from typing import List, Dict, Any
from dataset.loader import DatasetLoader
from target.factory import get_model_target
from evaluators.base import BaseEvaluator
from core.runner import EvaluationRunner
from reports.reporter import Reporter


class ModelComparison:
    def __init__(self, dataset_path: str, evaluators: Dict[str, BaseEvaluator]):
        self.dataset = DatasetLoader.from_json(dataset_path)
        self.evaluators = evaluators
        self.reporter = Reporter()

    async def compare(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_results = {}

        for cfg in configs:
            name = cfg.get("name", f"{cfg['provider']}_{cfg['model']}")
            print(f"\n>>> Running: {name}")

            target = get_model_target(
                cfg["provider"], cfg["model"], **cfg.get("kwargs", {})
            )

            runner = EvaluationRunner(
                target, max_concurrent=cfg.get("max_concurrent", 5)
            )

            results = await runner.run(
                self.dataset,
                self.evaluators,
                cfg.get("system_prompt"),
            )

            self.reporter.print_table(results, runner.metrics)

            all_results[name] = {
                "results": results,
                "metrics": runner.metrics.summary(),
            }

        print("\n" + "=" * 70)
        print(f"{'MODEL':<25} {'PASS RATE':<12} {'AVG SCORE':<12} {'AVG LATENCY':<12}")
        print("-" * 70)
        for name, data in all_results.items():
            m = data["metrics"]
            print(
                f"{name:<25} {m['pass_rate']:<12.2%} {m['avg_score']:<12.3f} {m['avg_latency_ms']:<12.1f}"
            )
        print("=" * 70)

        return all_results
