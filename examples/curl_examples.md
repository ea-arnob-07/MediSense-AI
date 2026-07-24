# API Examples

## Health
```bash
curl http://localhost:8000/health
```

## Predict
```bash
curl -X POST "http://localhost:8000/predict?top_k=5" \
  -H "Content-Type: application/json" \
  --data @examples/sample_patient.json
```

## Download PDF report
```bash
curl -X POST http://localhost:8000/report/pdf \
  -H "Content-Type: application/json" \
  --data @examples/sample_patient.json \
  --output prediction_report.pdf
```

Interactive API documentation is available at `http://localhost:8000/docs`.
