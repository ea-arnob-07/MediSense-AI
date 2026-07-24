from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def prediction_log_record(result: dict[str, Any]) -> dict[str, Any]:
    """Privacy-minimized log record. Raw symptoms and vital signs are not stored."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "prediction_id": result["prediction_id"],
        "top_disease": result["predictions"][0]["disease"],
        "confidence": result["predictions"][0]["probability"],
        "risk_level": result["risk_assessment"]["risk_level"],
        "active_symptom_count": result["input_summary"]["active_symptom_count"],
        "uncertainty_status": result["uncertainty"]["status"],
        "model_version": result["model_version"],
    }


def summarize_logs(path: Path, limit: int = 10000) -> dict[str, Any]:
    if not path.exists():
        return {"records": 0, "message": "Prediction logging is disabled or no records exist."}
    rows = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    rows = rows[-limit:]
    risks = Counter(row.get("risk_level") for row in rows)
    diseases = Counter(row.get("top_disease") for row in rows)
    confidences = [float(row.get("confidence", 0)) for row in rows]
    return {
        "records": len(rows),
        "risk_distribution": dict(risks),
        "top_predicted_diseases": diseases.most_common(10),
        "mean_confidence": sum(confidences) / len(confidences) if confidences else None,
    }
