from app.config import settings
from app.predictor import DiseasePredictor


def test_predictor_returns_ranked_differential():
    predictor = DiseasePredictor(settings.model_path)
    result = predictor.predict({"age": 25, "sex": "Male", "symptoms": {"Fever": 4, "Headache": 3, "Body_Ache": 4, "Rash": 2}, "temperature_c": 39.0}, top_k=5)
    assert len(result["predictions"]) == 5
    assert result["predictions"][0]["probability"] >= result["predictions"][1]["probability"]
    assert "risk_assessment" in result
    assert "care_guidance" in result
