# MediSense AI - Professional Disease Prediction & Triage System

MediSense AI is a complete, production-style educational health assessment project built on the expanded dataset:

- 25,000 synthetic patient records
- 179 disease classes
- 208 symptoms with severity levels from 0 to 5
- Demographics, history, vitals, measurements, and symptom duration
- Calibrated top-5 differential predictions
- Risk level and urgency screening
- Emergency red-flag override
- Explanations using matched disease-signature symptoms
- General care navigation and medication-safety warnings
- FastAPI REST API, bilingual responsive web interface, Streamlit dashboard, CLI, and bilingual PDF report
- Batch prediction, optional feedback loop, drift screen, Prometheus metrics, tests, Docker

> **Medical warning:** This is an educational prototype trained on synthetic data. It is not clinically validated and must not be used as a diagnosis, treatment recommendation, or replacement for a licensed healthcare professional.

## Model performance on the held-out synthetic test set

The generated `artifacts/model_metadata.json` contains exact results. The included trained model achieved approximately:

| Metric | Score |
|---|---:|
| Top-1 accuracy | 94.8% |
| Macro F1 | 94.8% |
| Top-3 accuracy | 99.0% |
| Top-5 accuracy | 99.6% |
| Expected calibration error | 1.5% |

These figures measure performance on this synthetic dataset only. They do not estimate accuracy in real patients.

## Quick start on Windows CMD

```bat
cd MediSense_AI_Professional_Disease_Prediction_System
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The trained model is already included. Start the API:

```bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- Main web app: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

Start the full dashboard in another CMD window:

```bat
cd MediSense_AI_Professional_Disease_Prediction_System
.venv\Scripts\activate
streamlit run dashboard\streamlit_app.py
```

Open `http://localhost:8501`.

## Retrain the model

```bat
python training\train_model.py
python training\model_audit.py
```

Retraining and auditing produce:

- `artifacts/disease_ensemble.joblib`
- `artifacts/model_metadata.json`
- `artifacts/MODEL_CARD.md`
- `artifacts/classification_report.csv`
- `artifacts/confusion_matrix.csv`
- Test-performance, reliability, support-vs-F1, feature, and subgroup plots
- Data-quality, subgroup, feature-schema, and confusion audit files

## CLI prediction

```bat
python cli.py examples\sample_patient.json --output result.json
```

## Main API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Readiness and model status |
| `GET /metadata` | Model metrics, counts, input options |
| `GET /symptoms` | Search symptom dictionary |
| `GET /diseases` | Search disease profiles |
| `GET /translations` | English-Bangla symptom, disease, category, risk, and urgency dictionaries |
| `POST /predict` | Single-patient differential prediction |
| `POST /batch-predict` | Batch JSON prediction |
| `POST /report/pdf` | Generate PDF result report |
| `POST /monitoring/drift-check` | Population input-drift screen |
| `GET /monitoring/summary` | Privacy-minimized operational summary |
| `POST /feedback` | Store de-identified confirmed-outcome feedback |
| `GET /metrics` | Prometheus metrics |

## Project structure

```text
app/            FastAPI, prediction engine, triage, guidance, reports, web UI
artifacts/      Trained model, metrics, model card, evaluation outputs
dashboard/      Streamlit application
data/           Expanded dataset and dictionaries
docs/           Architecture, deployment, and safety documentation
examples/       JSON requests, cURL, and Postman collection
notebooks/      EDA and training walkthrough
scripts/        Windows and Linux launch scripts
tests/          API, model, and safety-rule tests
training/       Reproducible model-training and model-audit pipelines
```

## Safety design

Prediction is intentionally separated from emergency triage. Even when model confidence is low, the safety layer can flag severe breathing difficulty, low oxygen, loss of consciousness, stroke signs, severe chest pain patterns, major bleeding, seizures, self-harm thoughts, and extreme measurements.

Public emergency guidance used as a reference:

- MedlinePlus emergency symptoms: https://medlineplus.gov/ency/article/001927.htm
- CDC stroke warning signs: https://www.cdc.gov/stroke/signs-symptoms/index.html
- WHO dengue warning signs: https://www.who.int/news-room/questions-and-answers/item/dengue-and-severe-dengue
- NHS heart-attack emergency signs: https://www.nhs.uk/conditions/heart-attack/

Read `docs/SAFETY_AND_LIMITATIONS.md` and `artifacts/MODEL_CARD.md` before using or presenting the system.

## Modern multi-step web experience

The main FastAPI web application now includes a fully redesigned, responsive dark-purple interface:

1. Animated landing and project overview
2. One-page bilingual patient profile with demographics, clinical background, Fahrenheit-to-Celsius conversion, feet/inches-to-centimeter conversion, optional-vital defaults, live validation, and automatic BMI calculation
3. Searchable English-Bangla symptom workspace with categories, severity scoring, compact cards enabled by default, selected-symptom analytics, and smooth page transitions
4. Rich bilingual analysis dashboard with a 3D confidence ring, animated clinical-risk dial, bilingual disease probabilities, vital-sign chart, severity trend, explainable evidence, care guidance, print, and a patient-profile PDF report
5. Responsive desktop, tablet, mobile, reduced-motion, and print layouts

The frontend uses native HTML, CSS, SVG, Canvas, and JavaScript without requiring a separate Node.js build process or external UI library.

The PDF generator uses a shaping-capable Bengali font when both a supported system font and `uharfbuzz` are available. If either requirement is missing, the report automatically switches to clean English-only text instead of showing broken boxes or malformed Bengali glyphs. Common Windows Nirmala UI and Linux Noto/Lohit Bengali font locations are detected automatically, with optional custom paths available in `.env.example`.

The footer includes direct LinkedIn, GitHub, and Facebook profile links for the developer.

### Interface credit

**Designed & Developed by Estiuk Arafat Arnob**
