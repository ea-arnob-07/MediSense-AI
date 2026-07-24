# Expanded Disease Prediction Dataset

Generated: 2026-07-23T17:13:04
Random seed: 20260723

## Package contents
- disease_prediction_dataset_expanded.csv: full wide-format dataset
- disease_profiles.csv: disease catalogue and signature symptoms
- symptom_dictionary.csv: symptom definitions and 0-5 severity scale
- disease_prediction_dataset_package.xlsx: formatted workbook with dictionaries, summaries, original data, and a model-data sample

## Dataset summary
- Rows: 25,000
- Diseases/conditions: 179
- Symptom severity columns: 208
- Uploaded rows preserved and augmented: 1,000
- Emergency red-flag rows: 3,670

## Severity coding
0 = absent, 1 = very mild, 2 = mild, 3 = moderate, 4 = severe, 5 = very severe/critical.

## Important safety limitation
This is a synthetic, medically informed educational dataset. It is not clinical evidence, not a diagnostic device, and not suitable for patient care without physician review, ethics approval, external validation, bias testing, calibration, and prospective clinical evaluation. Symptom-only systems cannot provide a perfect diagnosis because many conditions overlap, some diseases are asymptomatic, and diagnosis may require history, examination, laboratory tests, imaging, and clinical judgment.

## Leakage guidance
For a disease classifier, exclude Case_ID, Disease, Disease_Category, Disease_Severity, Emergency_Red_Flag and Urgency_Level from input features unless the research question explicitly needs them. Keep Train/Validation/Test as a split marker, not a predictive feature.

## Suggested evaluation
Use macro F1, weighted F1, per-class recall, top-3 accuracy, calibration error, confusion matrix, and emergency-condition sensitivity. Report performance separately by age group and sex.

## Reference starting points
- https://medlineplus.gov/encyclopedia.html
- https://medlineplus.gov/healthtopics.html
- https://medlineplus.gov/symptoms.html
- https://www.nhs.uk/symptoms/
- https://111.nhs.uk/
- https://www.who.int/news-room/fact-sheets/detail/sepsis
- https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-%28covid-19%29
