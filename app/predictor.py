from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.special import softmax
from sklearn.preprocessing import normalize

from app.i18n_bn import category_bn, disease_bn, symptom_bn
from app.recommendations import build_guidance
from app.triage import assess_triage


class DiseasePredictor:
    def __init__(self, model_path: str | Path, emergency_number: str = "999") -> None:
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}. Run: python training/train_model.py")
        self.artifact: dict[str, Any] = joblib.load(self.model_path)
        self.pipeline = self.artifact["pipeline"]
        self.classes = np.asarray(self.artifact["classes"])
        self.symptoms: list[str] = list(self.artifact["symptoms"])
        self.features: list[str] = list(self.artifact["features"])
        self.profiles: dict[str, dict[str, Any]] = self.artifact["disease_profiles"]
        self.symptom_metadata: dict[str, dict[str, Any]] = self.artifact["symptom_metadata"]
        self.defaults: dict[str, Any] = self.artifact["defaults"]
        self.emergency_number = emergency_number

    @staticmethod
    def display_name(value: str) -> str:
        return value.replace("_", " ")

    def _to_feature_row(self, patient: dict[str, Any]) -> pd.DataFrame:
        row = dict(self.defaults)
        mapping = {
            "age": "Age",
            "sex": "Sex",
            "pregnancy_status": "Pregnancy_Status",
            "smoking_status": "Smoking_Status",
            "comorbidity_1": "Comorbidity_1",
            "comorbidity_2": "Comorbidity_2",
            "symptom_duration_days": "Symptom_Duration_Days",
            "onset_type": "Onset_Type",
            "temperature_c": "Temperature_C",
            "heart_rate_bpm": "Heart_Rate_BPM",
            "respiratory_rate_bpm": "Respiratory_Rate_BPM",
            "spo2_percent": "SpO2_Percent",
            "systolic_bp": "Systolic_BP",
            "diastolic_bp": "Diastolic_BP",
            "bmi": "BMI",
            "random_glucose_mg_dl": "Random_Glucose_mg_dL",
            "pain_score_0_10": "Pain_Score_0_10",
        }
        for input_name, feature_name in mapping.items():
            if input_name in patient and patient[input_name] is not None:
                row[feature_name] = patient[input_name]
        unknown = []
        for symptom, severity in patient.get("symptoms", {}).items():
            if symptom in self.symptoms:
                row[symptom] = int(severity)
            else:
                unknown.append(symptom)
        frame = pd.DataFrame([row], columns=self.features)
        frame.attrs["unknown_symptoms"] = unknown
        return frame

    def _probabilities(self, frame: pd.DataFrame) -> np.ndarray:
        nb_prob = self.pipeline.predict_proba(frame[self.features])
        x = frame[self.symptoms].to_numpy(dtype=np.float32)
        idf = np.asarray(self.artifact["prototype_idf"], dtype=np.float32)
        prototype_means = np.asarray(self.artifact["prototype_means_weighted"], dtype=np.float32)
        prototype_score = normalize(x * np.sqrt(idf)) @ prototype_means.T
        prototype_prob = softmax(prototype_score / float(self.artifact["prototype_temperature"]), axis=1)
        weight = float(self.artifact["nb_weight"])
        combined = np.clip(weight * nb_prob + (1.0 - weight) * prototype_prob, 1e-12, 1.0)
        return softmax(np.log(combined) / float(self.artifact["calibration_temperature"]), axis=1)

    def _explain_prediction(self, disease: str, patient_symptoms: dict[str, int]) -> dict[str, Any]:
        profile = self.profiles.get(disease, {})
        signature = [x.strip() for x in str(profile.get("Signature_Symptoms", "")).split(",") if x.strip()]
        matched = [
            {
                "symptom": x,
                "display": self.display_name(x),
                "display_bn": symptom_bn(x),
                "severity": int(patient_symptoms.get(x, 0)),
            }
            for x in signature if int(patient_symptoms.get(x, 0)) > 0
        ]
        missing = [
            {"symptom": x, "display": self.display_name(x), "display_bn": symptom_bn(x)}
            for x in signature if int(patient_symptoms.get(x, 0)) == 0
        ]
        return {
            "matched_signature_symptoms": matched,
            "missing_signature_symptoms": missing,
            "signature_match_ratio": round(len(matched) / len(signature), 3) if signature else None,
        }

    def predict(self, patient: dict[str, Any], top_k: int = 5) -> dict[str, Any]:
        frame = self._to_feature_row(patient)
        probabilities = self._probabilities(frame)[0]
        order = np.argsort(probabilities)[::-1][: max(1, min(top_k, 10))]
        active = {k: int(v) for k, v in patient.get("symptoms", {}).items() if int(v) > 0 and k in self.symptoms}
        predictions = []
        for index in order:
            disease = str(self.classes[index])
            profile = self.profiles.get(disease, {})
            item = {
                "disease": disease,
                "disease_display": self.display_name(disease),
                "disease_display_bn": disease_bn(disease),
                "probability": round(float(probabilities[index]), 6),
                "category": profile.get("Category"),
                "category_bn": category_bn(profile.get("Category")),
                "base_urgency": profile.get("Base_Urgency", "Routine"),
                "typical_duration_days": profile.get("Typical_Duration_Days"),
                "explanation": self._explain_prediction(disease, active),
            }
            predictions.append(item)

        max_probability = float(probabilities[order[0]])
        sorted_probs = np.sort(probabilities)[::-1]
        margin = float(sorted_probs[0] - sorted_probs[1]) if len(sorted_probs) > 1 else max_probability
        entropy = float(-np.sum(probabilities * np.log(np.clip(probabilities, 1e-12, 1))))
        normalized_entropy = entropy / math.log(len(probabilities))
        unknown_symptoms = frame.attrs.get("unknown_symptoms", [])

        if len(active) < 2 or max_probability < 0.25 or normalized_entropy > 0.75:
            uncertainty_status = "high"
        elif max_probability < 0.60 or margin < 0.15:
            uncertainty_status = "moderate"
        else:
            uncertainty_status = "low"

        triage = assess_triage(patient, predictions).as_dict()
        guidance = build_guidance(patient, predictions, triage, self.emergency_number)
        result = {
            "prediction_id": str(uuid.uuid4()),
            "generated_at": datetime.now(UTC).isoformat(),
            "model_version": self.artifact["model_version"],
            "predictions": predictions,
            "risk_assessment": triage,
            "care_guidance": guidance,
            "uncertainty": {
                "status": uncertainty_status,
                "top_probability": round(max_probability, 6),
                "top_two_margin": round(margin, 6),
                "normalized_entropy": round(normalized_entropy, 6),
                "unknown_symptoms": unknown_symptoms,
                "message": "Low confidence means the symptom pattern may not be well represented in the training data." if uncertainty_status != "low" else "The model found a comparatively clear pattern, but this is still not a diagnosis.",
            },
            "input_summary": {
                "active_symptom_count": len(active),
                "maximum_symptom_severity": max(active.values()) if active else 0,
                "active_symptoms": [
                    {
                        "symptom": k,
                        "display": self.display_name(k),
                        "display_bn": symptom_bn(k),
                        "severity": v,
                    }
                    for k, v in sorted(active.items(), key=lambda item: (-item[1], item[0]))
                ],
            },
            "disclaimer": "Educational decision-support output only. The dataset is synthetic and the model is not clinically validated, medically certified, or a substitute for examination, testing, diagnosis, or treatment by a licensed professional.",
        }
        return result

    def metadata(self) -> dict[str, Any]:
        categories = sorted({meta.get("Category", "Other") for meta in self.symptom_metadata.values()})
        disease_categories = sorted({profile.get("Category", "Other") for profile in self.profiles.values()})
        return {
            "model_version": self.artifact["model_version"],
            "metrics": self.artifact["metrics"],
            "symptom_count": len(self.symptoms),
            "disease_count": len(self.classes),
            "symptom_categories": categories,
            "disease_categories": disease_categories,
            "severity_scale": {"0": "absent", "1": "very mild", "2": "mild", "3": "moderate", "4": "severe", "5": "very severe/critical"},
            "input_options": self.artifact["input_options"],
            "disclaimer": "Synthetic educational model. Not clinically validated.",
        }
