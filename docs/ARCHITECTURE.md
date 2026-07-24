# System Architecture

```text
Web UI / Streamlit / CLI / External Client
                 |
              FastAPI
                 |
      Input validation and normalization
                 |
     +-----------+----------------+
     |                            |
Disease ensemble              Safety layer
- Multinomial NB              - Red-flag rules
- Prototype similarity        - Vital checks
- Probability calibration     - Risk/urgency
     |                            |
     +------------+---------------+
                  |
      Differential diagnoses + explanation
                  |
     Recommendations and PDF reporting
                  |
 Optional privacy-minimized monitoring
```

## Design decisions

1. **Prediction and triage are separated.** A classifier can be uncertain, while a deterministic safety rule should still trigger on severe breathing difficulty, stroke signs, loss of consciousness, severe chest pain, self-harm thoughts, or extreme measurements.
2. **Top-k output instead of a single diagnosis.** Symptom overlap makes differential ranking more honest and useful.
3. **Calibration and uncertainty.** The API reports confidence, top-two margin, normalized entropy, unknown symptoms, and a simple out-of-distribution warning.
4. **No raw health data logging by default.** Optional logs store only prediction metadata, risk level, confidence, and model version.
5. **Reproducible training.** The `training/train_model.py` script rebuilds the artifact, metrics, reports, and plots from the included dataset.

## Production extensions before real clinical use

- Prospective clinical validation with representative real patient data
- Institutional review, medical-device regulatory assessment, and quality management
- Bias and subgroup performance analysis
- Calibrated prevalence for each geography and care setting
- External validation, silent deployment, and clinician-in-the-loop testing
- Secure identity, consent, encryption, retention policy, and audit controls
- Formal triage protocol validation and human-factors testing
