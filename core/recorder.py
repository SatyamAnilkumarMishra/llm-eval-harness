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

        self._file = open(self.path, "a", encoding="utf-8", buffering=1)
        self.buffer: List[Dict[str, Any]] = [] 

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
