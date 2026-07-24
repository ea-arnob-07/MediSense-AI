from __future__ import annotations

from typing import Any

import numpy as np


def check_batch_drift(patients: list[dict[str, Any]], artifact: dict[str, Any]) -> dict[str, Any]:
    symptoms = artifact["symptoms"]
    baseline = artifact.get("training_baseline", {})
    baseline_prevalence = baseline.get("symptom_prevalence", {})

    if len(patients) < 20:
        return {
            "status": "insufficient_sample",
            "message": "At least 20 records are recommended for a meaningful drift check.",
            "sample_size": len(patients),
        }

    current = {}
    for symptom in symptoms:
        current[symptom] = float(np.mean([int(p.get("symptoms", {}).get(symptom, 0)) > 0 for p in patients]))

    shifts = []
    for symptom in symptoms:
        base = float(baseline_prevalence.get(symptom, 0.0))
        delta = current[symptom] - base
        shifts.append({"symptom": symptom, "baseline": base, "current": current[symptom], "absolute_shift": abs(delta), "direction": "up" if delta > 0 else "down"})
    shifts.sort(key=lambda x: x["absolute_shift"], reverse=True)
    mean_shift = float(np.mean([x["absolute_shift"] for x in shifts]))
    status = "high" if mean_shift >= 0.15 else "moderate" if mean_shift >= 0.08 else "low"
    return {
        "status": status,
        "sample_size": len(patients),
        "mean_absolute_prevalence_shift": mean_shift,
        "top_shifted_symptoms": shifts[:15],
        "note": "This is a simple population drift screen, not a formal clinical performance audit.",
    }
