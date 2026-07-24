# MediSense AI - Professional UI Release

**Developed by Estiuk Arafat Arnob**

## Included improvements

- MediSense AI branding across the web UI, API, downloads, documentation, and PDF report.
- Slightly deeper dark-purple grading while preserving the original visual identity.
- Upgraded 3D overview experience with a more balanced heading scale, medical-cross identity marks, interactive lighting, glass cards, animated grid, scanning beam, a redesigned clinical engine status console, and reduced-motion support.
- Removed the interface volume control.
- Bilingual English-Bangla patient inputs, symptoms, categories, disease outputs, risk labels, and key analysis labels.
- Complete Bengali mappings for all 208 symptoms and all 179 disease classes.
- Fahrenheit input normalized to Celsius in the backend.
- Feet/inches input normalized to centimeters in the backend.
- Automatic BMI calculation from converted height and weight.
- Respiratory rate, oxygen saturation, systolic blood pressure, diastolic blood pressure, and random glucose are optional. Normal defaults are applied when omitted.
- Required vital inputs remain temperature, heart rate, and pain score.
- Redesigned animated clinical-risk dial with progressive arc, dynamic needle, risk glow, and low/moderate/high/critical states.
- PDF assessment report with patient name, age, sex, height, weight, BMI, temperature, vitals, symptoms, disease probabilities, risk assessment, care guidance, report ID, page numbers, and developer credit. Bengali is used only when a shaping-capable system font is available; otherwise the PDF safely falls back to English-only text.
- Removed the result-page JSON download button while keeping JSON API endpoints available for development and integration.
- Compact symptom cards are now the default view, with the larger comfortable view still available from the display toggle.
- Added LinkedIn, GitHub, and Facebook profile icons below the developer credit.
- Accessibility and interaction fixes, including decorative-layer pointer handling and reduced-motion behavior.
- Pointer-driven 3D effects are requestAnimationFrame-throttled, and ambient rendering pauses while the tab is hidden.

## Safety note

This project is an educational decision-support prototype trained on synthetic data. It is not clinically validated and must not be used as a confirmed diagnosis or as a substitute for a licensed healthcare professional.
