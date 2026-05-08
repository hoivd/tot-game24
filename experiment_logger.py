import json
import time
from pathlib import Path
from datetime import datetime


class ExperimentLogger:
    def __init__(self, config, output_dir="results"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.output_path = self.output_dir / f"run_{timestamp}.json"

        self.data = {
            "run_id": timestamp,
            "config": config,
            "results": []
        }

    @staticmethod
    def start_case():
        return time.perf_counter()

    def end_case(self, record, start_time):
        record["runtime_sec"] = round(
            time.perf_counter() - start_time,
            6
        )
        self.data["results"].append(record)

    def save(self):
        self.output_path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"Saved results to: {self.output_path}")