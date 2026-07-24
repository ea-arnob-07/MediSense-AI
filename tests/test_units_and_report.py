from fastapi.testclient import TestClient

from app.main import app
from app.schemas import NORMAL_DEFAULTS, PatientInput

client = TestClient(app)


def test_fahrenheit_and_feet_inches_are_normalized():
    patient = PatientInput(
        temperature_f=98.6,
        height_feet=5,
        height_inches=7,
        weight_kg=68,
        symptoms={"Fever": 2, "Cough": 2},
    )
    assert patient.temperature_c == 37.0
    assert patient.height_cm == 170.18
    assert patient.bmi == 23.5


def test_optional_vitals_use_normal_defaults_when_omitted():
    patient = PatientInput(
        temperature_f=98.6,
        height_feet=5,
        height_inches=7,
        weight_kg=68,
    )
    for field, expected in NORMAL_DEFAULTS.items():
        assert getattr(patient, field) == expected


def test_bilingual_symptom_and_disease_output_and_pdf():
    payload = {
        "patient_name": "Test Patient",
        "age": 30,
        "sex": "Female",
        "pregnancy_status": "No",
        "smoking_status": "Never",
        "symptom_duration_days": 3,
        "onset_type": "Sudden",
        "temperature_f": 102.2,
        "heart_rate_bpm": 102,
        "pain_score_0_10": 5,
        "height_feet": 5,
        "height_inches": 4,
        "weight_kg": 56,
        "provided_measurements": [],
        "symptoms": {"Fever": 4, "Severe_Headache": 3, "Body_Ache": 4, "Rash": 2},
    }
    prediction = client.post("/predict", json=payload)
    assert prediction.status_code == 200
    body = prediction.json()
    assert body["predictions"][0]["disease_display_bn"]
    assert body["input_summary"]["active_symptoms"][0]["display_bn"]

    report = client.post("/report/pdf", json=payload)
    assert report.status_code == 200
    assert report.headers["content-type"].startswith("application/pdf")
    assert report.content.startswith(b"%PDF")
    assert len(report.content) > 7_000
