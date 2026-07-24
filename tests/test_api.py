from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_predict_endpoint():
    response = client.post("/predict", json={"age": 30, "sex": "Female", "symptoms": {"Cough": 3, "Fever": 2, "Runny_Nose": 2}})
    assert response.status_code == 200
    body = response.json()
    assert len(body["predictions"]) == 5
