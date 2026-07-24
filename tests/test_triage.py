from app.triage import assess_triage


def test_stroke_red_flag_is_critical():
    patient = {"spo2_percent": 98, "respiratory_rate_bpm": 16, "heart_rate_bpm": 80, "systolic_bp": 120, "diastolic_bp": 80, "temperature_c": 37, "random_glucose_mg_dl": 100, "symptoms": {"Facial_Droop": 3, "One_Sided_Weakness": 3}}
    result = assess_triage(patient, []).as_dict()
    assert result["emergency"] is True
    assert result["risk_level"] == "Critical"


def test_low_risk_without_red_flags():
    patient = {"spo2_percent": 98, "respiratory_rate_bpm": 16, "heart_rate_bpm": 80, "systolic_bp": 120, "diastolic_bp": 80, "temperature_c": 37, "random_glucose_mg_dl": 100, "symptoms": {"Runny_Nose": 1}}
    result = assess_triage(patient, []).as_dict()
    assert result["emergency"] is False
    assert result["risk_level"] == "Low"
