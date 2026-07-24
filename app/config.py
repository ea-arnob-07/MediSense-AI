from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def _resolve_path(value: str, default: str) -> Path:
    path = Path(os.getenv(value, default))
    return path if path.is_absolute() else BASE_DIR / path


@dataclass(frozen=True)
class Settings:
    model_path: Path = _resolve_path("MODEL_PATH", "artifacts/disease_ensemble.joblib")
    emergency_number: str = os.getenv("EMERGENCY_NUMBER", "999")
    enable_prediction_logging: bool = os.getenv("ENABLE_PREDICTION_LOGGING", "false").lower() == "true"
    prediction_log_path: Path = _resolve_path("PREDICTION_LOG_PATH", "logs/predictions.jsonl")
    feedback_log_path: Path = _resolve_path("FEEDBACK_LOG_PATH", "logs/feedback.jsonl")
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "100"))
    api_title: str = os.getenv("API_TITLE", "MediSense AI - Intelligent Health Assessment API")


settings = Settings()
