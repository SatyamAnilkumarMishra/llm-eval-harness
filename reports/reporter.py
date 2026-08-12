import csv
import json
import os
from typing import List, Dict, Any
from core.metrics import MetricsTracker


class Reporter:
    def __init__(self, output_dir: str = "reports/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def print_table(self, results: List[Dict[str, Any]], metrics: MetricsTracker):
        print("\n" + "=" * 90)
        print(
            f"{'ID':<12} {'SCORE':<8} {'PASS':<6} {'LATENCY':<10} {'REASONING':<50}"
        )
        print("-" * 90)
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            reasoning = r["reasoning"]
            if len(reasoning) > 48:
                reasoning = reasoning[:46] + ".."
            print(
                f"{r['id']:<12} {r['score']:<8.2f} {status:<6} {r['latency_ms']:<10.1f} {reasoning:<50}"
            )
        print("-" * 90)
        s = metrics.summary()
        print(
            f"\nSUMMARY: {s['passed']}/{s['total_samples']} passed | "
            f"Pass Rate: {s['pass_rate']:.2%} | Avg Score: {s['avg_score']:.3f} | "
            f"Avg Latency: {s['avg_latency_ms']}ms"
        )
        print("=" * 90 + "\n")

    def to_csv(self, results: List[Dict[str, Any]], filename: str = "report.csv") -> str:
        path = os.path.join(self.output_dir, filename)
        if not results:
            return path

        keys = list(results[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in results:
                flat = {
                    k: json.dumps(v) if isinstance(v, (dict, list)) else v
                    for k, v in r.items()
                }
                writer.writerow(flat)
        return path
