from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


NORMAL_DEFAULTS = {
    "respiratory_rate_bpm": 16,
    "spo2_percent": 98,
    "systolic_bp": 120,
    "diastolic_bp": 80,
    "random_glucose_mg_dl": 100,
}


class PatientInput(BaseModel):
    """Patient input accepted by both the browser UI and the prediction API.

    The public UI can submit Fahrenheit and feet/inches. This model normalizes
    those values to Celsius and centimeters before prediction. Optional vital
    readings are replaced with conservative normal defaults when omitted.
    """

    model_config = ConfigDict(extra="forbid")

    patient_name: str | None = Field(default=None, max_length=80)
    age: int = Field(default=35, ge=0, le=120)
    sex: str = Field(default="Other")
    pregnancy_status: str = Field(default="Not_Applicable")
    smoking_status: str = Field(default="Never")
    comorbidity_1: str | None = None
    comorbidity_2: str | None = None
    symptom_duration_days: int = Field(default=1, ge=0, le=3650)
    onset_type: str = Field(default="Gradual")

    # UI-friendly units. Backend normalization fills temperature_c/height_cm.
    temperature_f: float | None = Field(default=None, ge=86.0, le=113.0)
    temperature_c: float | None = Field(default=None, ge=30.0, le=45.0)
    height_feet: int | None = Field(default=None, ge=1, le=8)
    height_inches: float | None = Field(default=None, ge=0.0, lt=12.0)
    height_cm: float | None = Field(default=None, ge=50.0, le=250.0)
    weight_kg: float | None = Field(default=None, ge=2.0, le=400.0)

    heart_rate_bpm: int = Field(default=80, ge=20, le=250)
    respiratory_rate_bpm: int | None = Field(default=None, ge=4, le=80)
    spo2_percent: int | None = Field(default=None, ge=50, le=100)
    systolic_bp: int | None = Field(default=None, ge=40, le=280)
    diastolic_bp: int | None = Field(default=None, ge=20, le=180)
    bmi: float | None = Field(default=None, ge=8.0, le=80.0)
    random_glucose_mg_dl: int | None = Field(default=None, ge=20, le=800)
    pain_score_0_10: int = Field(default=0, ge=0, le=10)
    symptoms: dict[str, int] = Field(default_factory=dict)
    provided_measurements: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_units_and_defaults(self) -> "PatientInput":
        if self.temperature_f is not None:
            self.temperature_c = round((self.temperature_f - 32.0) * 5.0 / 9.0, 2)
        elif self.temperature_c is None:
            self.temperature_c = 37.0
            self.temperature_f = 98.6
        else:
            self.temperature_f = round((self.temperature_c * 9.0 / 5.0) + 32.0, 2)

        if self.height_feet is not None:
            inches = self.height_inches or 0.0
            self.height_cm = round((self.height_feet * 30.48) + (inches * 2.54), 2)
        elif self.height_cm is not None:
            total_inches = self.height_cm / 2.54
            self.height_feet = int(total_inches // 12)
            self.height_inches = round(total_inches - (self.height_feet * 12), 1)

        for field_name, normal_value in NORMAL_DEFAULTS.items():
            if getattr(self, field_name) is None:
                setattr(self, field_name, normal_value)

        if self.height_cm and self.weight_kg:
            self.bmi = round(self.weight_kg / ((self.height_cm / 100.0) ** 2), 1)
        elif self.bmi is None:
            self.bmi = 23.0

        return self

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, value: dict[str, int]) -> dict[str, int]:
        cleaned: dict[str, int] = {}
        for name, severity in value.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Symptom names must be non-empty strings")
            if isinstance(severity, bool) or not isinstance(severity, int):
                raise ValueError(f"Severity for {name} must be an integer")
            if severity < 0 or severity > 5:
                raise ValueError(f"Severity for {name} must be between 0 and 5")
            cleaned[name.strip()] = severity
        return cleaned


class BatchInput(BaseModel):
    patients: list[PatientInput]


class FeedbackInput(BaseModel):
    prediction_id: str
    confirmed_disease: str
    useful: bool | None = None
    notes: str | None = Field(default=None, max_length=1000)


class DriftInput(BaseModel):
    patients: list[PatientInput]


class GenericResponse(BaseModel):
    data: dict[str, Any]
