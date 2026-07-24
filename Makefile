.PHONY: install train api dashboard test lint docker
install:
	python -m pip install -r requirements.txt
train:
	python training/train_model.py
	python training/model_audit.py
api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
dashboard:
	streamlit run dashboard/streamlit_app.py
test:
	pytest
lint:
	ruff check .
docker:
	docker compose up --build
