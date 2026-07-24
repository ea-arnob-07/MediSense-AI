from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.config import settings
from app.predictor import DiseasePredictor


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a disease prediction from a JSON patient file")
    parser.add_argument("input", type=Path, help="Patient JSON file")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    patient = json.loads(args.input.read_text(encoding="utf-8"))
    result = DiseasePredictor(settings.model_path, settings.emergency_number).predict(patient, top_k=args.top_k)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Saved: {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
