from __future__ import annotations

import io
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.config import BASE_DIR, settings
from app.drift import check_batch_drift
from app.i18n_bn import CATEGORY_BN, DISEASE_BN, RISK_BN, SYMPTOM_BN, URGENCY_BN, category_bn, disease_bn, symptom_bn
from app.monitoring import append_jsonl, prediction_log_record, summarize_logs
from app.predictor import DiseasePredictor
from app.reporting import create_prediction_pdf
from app.schemas import BatchInput, DriftInput, FeedbackInput, PatientInput

PREDICTIONS = Counter("medical_predictions_total", "Total predictions", ["risk_level"])
LATENCY = Histogram("medical_prediction_seconds", "Prediction latency")


@lru_cache(maxsize=1)
def get_predictor() -> DiseasePredictor:
    return DiseasePredictor(settings.model_path, settings.emergency_number)


app = FastAPI(
    title=settings.api_title,
    version="1.0.0",
    description="Educational disease prediction, differential ranking, uncertainty, and conservative triage API.",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "app" / "static" / "index.html")


@app.get("/health")
def health() -> dict:
    predictor = get_predictor()
    return {"status": "ok", "model_version": predictor.artifact["model_version"], "model_loaded": True}


@app.get("/metadata")
def metadata() -> dict:
    return get_predictor().metadata()


@app.get("/symptoms")
def symptoms(query: str = Query(default=""), category: str | None = None, limit: int = Query(default=250, ge=1, le=250)) -> dict:
    predictor = get_predictor()
    q = query.lower().strip()
    rows = []
    for name in predictor.symptoms:
        meta = predictor.symptom_metadata.get(name, {})
        if q and q not in name.lower() and q not in name.replace("_", " ").lower():
            continue
        if category and meta.get("Category") != category:
            continue
        rows.append({"name": name, "display": predictor.display_name(name), "display_bn": symptom_bn(name), **meta})
    return {"count": len(rows[:limit]), "items": rows[:limit]}


@app.get("/diseases")
def diseases(query: str = Query(default=""), category: str | None = None, limit: int = Query(default=250, ge=1, le=250)) -> dict:
    predictor = get_predictor()
    q = query.lower().strip()
    rows = []
    for name, profile in predictor.profiles.items():
        if q and q not in name.lower() and q not in name.replace("_", " ").lower():
            continue
        if category and profile.get("Category") != category:
            continue
        rows.append({"name": name, "display": predictor.display_name(name), "display_bn": disease_bn(name), "category_bn": category_bn(profile.get("Category")), **profile})
    rows.sort(key=lambda item: item["display"])
    return {"count": len(rows[:limit]), "items": rows[:limit]}


@app.get("/translations")
def translations() -> dict:
    return {
        "symptoms": SYMPTOM_BN,
        "diseases": DISEASE_BN,
        "categories": CATEGORY_BN,
        "risk_levels": RISK_BN,
        "urgency": URGENCY_BN,
    }


@app.post("/predict")
def predict(payload: PatientInput, top_k: int = Query(default=5, ge=1, le=10)) -> dict:
    with LATENCY.time():
        result = get_predictor().predict(payload.model_dump(), top_k=top_k)
    PREDICTIONS.labels(result["risk_assessment"]["risk_level"]).inc()
    if settings.enable_prediction_logging:
        append_jsonl(settings.prediction_log_path, prediction_log_record(result))
    return result


@app.post("/batch-predict")
def batch_predict(payload: BatchInput, top_k: int = Query(default=3, ge=1, le=5)) -> dict:
    if len(payload.patients) > settings.max_batch_size:
        raise HTTPException(status_code=413, detail=f"Maximum batch size is {settings.max_batch_size}")
    results = [get_predictor().predict(patient.model_dump(), top_k=top_k) for patient in payload.patients]
    return {"count": len(results), "results": results}


@app.post("/report/pdf")
def report_pdf(payload: PatientInput) -> Response:
    result = get_predictor().predict(payload.model_dump(), top_k=5)
    pdf = create_prediction_pdf(result, payload.model_dump())
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=MediSense_Report_{result['prediction_id']}.pdf"},
    )


@app.post("/monitoring/drift-check")
def drift_check(payload: DriftInput) -> dict:
    if len(payload.patients) > 1000:
        raise HTTPException(status_code=413, detail="Maximum drift-check batch size is 1000")
    return check_batch_drift([patient.model_dump() for patient in payload.patients], get_predictor().artifact)


@app.get("/monitoring/summary")
def monitoring_summary() -> dict:
    return summarize_logs(settings.prediction_log_path)


@app.post("/feedback")
def feedback(payload: FeedbackInput) -> dict:
    append_jsonl(settings.feedback_log_path, payload.model_dump())
    return {"status": "stored", "message": "Feedback stored without patient-identifying data."}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
