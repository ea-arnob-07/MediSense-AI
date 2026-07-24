# Safety and Limitations

This project is a production-style software demonstration, not a clinically approved medical product.

## What it can do

- Rank possible diseases represented in the synthetic training dataset
- Show top-5 differential possibilities and calibrated model probabilities
- Match entered symptoms to each disease's synthetic signature profile
- Screen for conservative emergency warning signs
- Explain uncertainty and unknown inputs
- Produce general care-navigation guidance and a downloadable report

## What it cannot do

- Confirm or rule out a diagnosis
- Replace history-taking, examination, laboratory tests, imaging, or clinician judgment
- Recommend a specific drug, dose, or treatment plan
- Guarantee safety because the model has high synthetic test accuracy
- Generalize reliably to real patients without clinical validation

## Emergency reference basis

The safety layer includes warning patterns consistent with public emergency guidance, including severe breathing difficulty, loss of consciousness, persistent/severe chest pain, stroke warning signs, severe bleeding, seizures, and self-harm thoughts. Sources:

- https://medlineplus.gov/ency/article/001927.htm
- https://www.nhs.uk/conditions/heart-attack/
- https://www.cdc.gov/stroke/signs-symptoms/index.html
- https://www.who.int/news-room/questions-and-answers/item/dengue-and-severe-dengue

Thresholds in the code remain educational heuristics and require local clinical validation.
