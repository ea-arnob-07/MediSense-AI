# Deployment Guide

## Local development

```bash
python -m venv .venv
```

Windows CMD:
```bat
.venv\Scripts\activate
pip install -r requirements.txt
python training\train_model.py
uvicorn app.main:app --reload
```

Open:
- Web interface: http://localhost:8000
- OpenAPI docs: http://localhost:8000/docs
- Prometheus metrics: http://localhost:8000/metrics

Dashboard in another terminal:
```bat
.venv\Scripts\activate
streamlit run dashboard\streamlit_app.py
```

## Docker

```bash
docker compose up --build
```

- API and web UI: http://localhost:8000
- Streamlit dashboard: http://localhost:8501

## Environment settings

Copy `.env.example` to `.env` and modify values. Prediction logging is off by default. For a public deployment, add authentication, HTTPS, rate limiting, encrypted storage, secret management, and a legally reviewed privacy policy.
