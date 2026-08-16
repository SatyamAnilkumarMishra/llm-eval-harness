"""
Persists raw per-sample results to a JSONL file.

FIXED BUG (from the original version): results used to be buffered in
memory and only written to disk on an explicit `.flush()` call at the
very end of a run. If a 200-sample run crashed on sample 150 — a real
possibility with flaky network calls — every one of those 150 completed
results was lost, because nothing had touched disk yet.

The fix: open the output file once, in append mode, at construction
time, and write each result to disk immediately in `save()`. `flush()`
still exists (for the return-path filename main.py prints), but it's no
longer load-bearing for correctness — you can `tail -f` the run file
mid-run, and a crash only loses the *in-flight* sample, not everything
before it.

LEARNING POINT: this is a general principle for anything long-running —
prefer "write as you go" over "buffer then write" whenever a partial
result still has value. Buffering is fine for reports (report.csv is
still built at the end from an in-memory `results` list, and that's
okay — reports need the *whole* run to be meaningful anyway).
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List


class ResultRecorder:
    def __init__(self, output_dir: str = "reports/results", run_id: str = None):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(self.output_dir, f"run_{self.run_id}.jsonl")

        # Append mode + line-buffered so each save() is durable on disk
        # right away, not just sitting in a Python-level list.
        self._file = open(self.path, "a", encoding="utf-8", buffering=1)
        self.buffer: List[Dict[str, Any]] = []  # kept for callers that want the in-memory list too

    def save(self, result: Dict[str, Any]):
        self.buffer.append(result)
        self._file.write(json.dumps(result, ensure_ascii=False) + "\n")

    def flush(self, run_id: str = None) -> str:
        """Ensures everything is on disk and returns the run file's path.
        (Writing already happened per-sample in save(); this just closes
        out the file handle cleanly.)"""
        self._file.flush()
        return self.path

    def close(self):
        if not self._file.closed:
            self._file.close()
