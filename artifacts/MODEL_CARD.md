# Model Card

## Intended use
Educational disease-prediction and triage demonstration. It ranks possible conditions and highlights warning signs. It must not be used for autonomous diagnosis, treatment, medication decisions, emergency dispatch, or clinical care without professional validation and oversight.

## Data
- Synthetic, medically informed dataset
- Rows: 25,000
- Diseases: 179
- Symptoms: 208
- Severity scale: 0–5

## Model
Ensemble of calibrated Multinomial Naive Bayes and severity-profile cosine similarity. A deterministic safety layer separately evaluates emergency warning signs and abnormal measurements.

## Held-out test results
- Top-1 accuracy: 0.9484
- Macro F1: 0.9483
- Top-3 accuracy: 0.9897
- Top-5 accuracy: 0.9963
- Log loss: 0.1598
- Expected calibration error: 0.0155

These numbers measure fit to this synthetic dataset, not safety or accuracy in real patients.

## Key limitations
- The dataset does not represent a clinical population or verified diagnoses.
- Real symptoms may be incomplete, ambiguous, culturally described, or affected by comorbidities and medicines.
- Disease prevalence and severity differ by geography, age, season, and healthcare setting.
- A high probability is not proof of disease. A low probability does not rule it out.
- The triage thresholds are conservative educational heuristics, not a validated triage protocol.

## Safety references
- MedlinePlus, recognizing medical emergencies: https://medlineplus.gov/ency/article/001927.htm
- CDC, stroke signs and symptoms: https://www.cdc.gov/stroke/signs-symptoms/index.html
- WHO, dengue warning signs: https://www.who.int/news-room/questions-and-answers/item/dengue-and-severe-dengue
- NHS, heart attack emergency symptoms: https://www.nhs.uk/conditions/heart-attack/
