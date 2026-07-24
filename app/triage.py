from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TriageResult:
    risk_level: str
    risk_score: int
    urgency: str
    emergency: bool
    red_flags: list[str]
    abnormal_vitals: list[str]
    rationale: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "urgency": self.urgency,
            "emergency": self.emergency,
            "red_flags": self.red_flags,
            "abnormal_vitals": self.abnormal_vitals,
            "rationale": self.rationale,
        }


def assess_triage(patient: dict[str, Any], top_predictions: list[dict[str, Any]]) -> TriageResult:
    """Conservative educational triage rules. They are not clinically validated."""

    symptoms = patient.get("symptoms", {})

    def s(name: str) -> int:
        return int(symptoms.get(name, 0) or 0)

    red_flags: list[str] = []
    abnormal: list[str] = []
    rationale: list[str] = []
    score = 0

    spo2 = int(patient.get("spo2_percent", 98))
    rr = int(patient.get("respiratory_rate_bpm", 16))
    hr = int(patient.get("heart_rate_bpm", 80))
    sbp = int(patient.get("systolic_bp", 120))
    dbp = int(patient.get("diastolic_bp", 80))
    temp = float(patient.get("temperature_c", 37.0))
    glucose = int(patient.get("random_glucose_mg_dl", 100))

    if spo2 <= 90:
        red_flags.append(f"Very low oxygen saturation ({spo2}%)")
    elif spo2 <= 93:
        abnormal.append(f"Low oxygen saturation ({spo2}%)")
        score += 3

    if rr >= 30:
        red_flags.append(f"Very rapid breathing ({rr}/min)")
    elif rr >= 24:
        abnormal.append(f"Rapid breathing ({rr}/min)")
        score += 2

    if sbp < 80:
        red_flags.append(f"Very low systolic blood pressure ({sbp} mmHg)")
    elif sbp < 90:
        abnormal.append(f"Low systolic blood pressure ({sbp} mmHg)")
        score += 3
    elif sbp >= 180 or dbp >= 120:
        abnormal.append(f"Very high blood pressure ({sbp}/{dbp} mmHg)")
        score += 3

    if hr >= 140 or hr <= 40:
        red_flags.append(f"Extreme heart rate ({hr} bpm)")
    elif hr >= 120 or hr <= 50:
        abnormal.append(f"Abnormal heart rate ({hr} bpm)")
        score += 2

    if temp >= 40.0:
        abnormal.append(f"Very high temperature ({temp:.1f}°C)")
        score += 3
    elif temp >= 39.0:
        abnormal.append(f"High temperature ({temp:.1f}°C)")
        score += 2

    if glucose < 50 or glucose >= 500:
        red_flags.append(f"Extreme random glucose reading ({glucose} mg/dL)")
    elif glucose < 70 or glucose >= 300:
        abnormal.append(f"Abnormal random glucose reading ({glucose} mg/dL)")
        score += 3

    if s("Loss_of_Consciousness") >= 1 or s("Fainting") >= 4:
        red_flags.append("Loss of consciousness or severe fainting")
    if s("Shortness_of_Breath") >= 5 or s("Blue_Lips") >= 1 or s("Stridor") >= 4:
        red_flags.append("Severe breathing difficulty or blue lips")
    if s("Chest_Pain") >= 4 and any(s(x) >= 2 for x in ["Cold_Sweat", "Jaw_Pain", "Nausea", "Shortness_of_Breath"]):
        red_flags.append("Severe chest pain with possible heart-attack features")
    if s("Facial_Droop") >= 2 or s("One_Sided_Weakness") >= 2 or s("Slurred_Speech") >= 2:
        red_flags.append("Possible stroke warning signs")
    if s("Seizure") >= 4:
        red_flags.append("Severe or ongoing seizure symptoms")
    if s("Lip_Tongue_Swelling") >= 2 and (s("Shortness_of_Breath") >= 2 or s("Wheezing") >= 3):
        red_flags.append("Possible severe allergic reaction affecting breathing")
    if s("Self_Harm_Thoughts") >= 1:
        red_flags.append("Thoughts of self-harm")
    if s("Coughing_Blood") >= 3 or s("Black_Stool") >= 4 or s("Blood_in_Stool") >= 4:
        red_flags.append("Possible major bleeding")
    if s("Severe_Headache") >= 5 and any(s(x) >= 2 for x in ["Neck_Stiffness", "Confusion", "Vision_Loss", "One_Sided_Weakness"]):
        red_flags.append("Severe headache with neurological warning signs")

    high_severity_count = sum(1 for v in symptoms.values() if int(v) >= 4)
    moderate_severity_count = sum(1 for v in symptoms.values() if int(v) >= 3)
    score += min(4, high_severity_count)
    if moderate_severity_count >= 5:
        score += 2
        rationale.append("Multiple moderate-to-severe symptoms")

    urgency_weight = {"Routine": 0, "See_Doctor_Soon": 2, "Urgent": 4, "Emergency": 6}
    for prediction in top_predictions[:3]:
        probability = float(prediction.get("probability", 0))
        base_urgency = str(prediction.get("base_urgency", "Routine"))
        if probability >= 0.15:
            added = urgency_weight.get(base_urgency, 0)
            score = max(score, added)
            if added:
                rationale.append(f"{prediction['disease_display']} profile has {base_urgency.lower()} base urgency")

    if red_flags:
        return TriageResult(
            risk_level="Critical",
            risk_score=max(10, score),
            urgency="Emergency care now",
            emergency=True,
            red_flags=list(dict.fromkeys(red_flags)),
            abnormal_vitals=abnormal,
            rationale=rationale,
        )
    if score >= 7:
        risk, urgency = "High", "Same-day urgent clinical assessment"
    elif score >= 3:
        risk, urgency = "Moderate", "Clinical review within 24–48 hours"
    else:
        risk, urgency = "Low", "Monitor and arrange routine care if symptoms persist or worsen"

    return TriageResult(
        risk_level=risk,
        risk_score=score,
        urgency=urgency,
        emergency=False,
        red_flags=[],
        abnormal_vitals=abnormal,
        rationale=rationale,
    )
