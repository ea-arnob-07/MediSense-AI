from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.predictor import DiseasePredictor
from app.reporting import create_prediction_pdf

st.set_page_config(page_title="Medical Decision Support", page_icon="🩺", layout="wide")


@st.cache_resource
def load_predictor() -> DiseasePredictor:
    return DiseasePredictor(settings.model_path, settings.emergency_number)


predictor = load_predictor()
metadata = predictor.metadata()

st.title("Medical Disease Prediction & Triage Demo")
st.caption("179 disease classes • 208 severity-based symptoms • differential ranking • uncertainty • safety triage")
st.warning("Educational prototype using synthetic data. It is not a diagnosis and is not clinically validated.")

with st.sidebar:
    st.header("Patient information")
    age = st.number_input("Age", 0, 120, 35)
    sex = st.selectbox("Sex", metadata["input_options"].get("Sex", ["Male", "Female", "Other"]))
    pregnancy = st.selectbox("Pregnancy status", metadata["input_options"].get("Pregnancy_Status", ["Not_Applicable"]))
    smoking = st.selectbox("Smoking status", metadata["input_options"].get("Smoking_Status", ["Never"]))
    onset = st.selectbox("Onset", metadata["input_options"].get("Onset_Type", ["Gradual", "Sudden"]))
    duration = st.number_input("Symptom duration (days)", 0, 3650, 2)
    pain = st.slider("Overall pain score", 0, 10, 0)
    with st.expander("Vitals and measurements"):
        temperature = st.number_input("Temperature °C", 30.0, 45.0, 37.0, 0.1)
        heart_rate = st.number_input("Heart rate", 20, 250, 80)
        respiratory_rate = st.number_input("Respiratory rate", 4, 80, 16)
        spo2 = st.number_input("SpO₂ %", 50, 100, 98)
        systolic = st.number_input("Systolic BP", 40, 280, 120)
        diastolic = st.number_input("Diastolic BP", 20, 180, 80)
        bmi = st.number_input("BMI", 8.0, 80.0, 23.0, 0.1)
        glucose = st.number_input("Random glucose mg/dL", 20, 800, 100)

st.subheader("Symptoms")
selected = st.multiselect(
    "Search and select symptoms",
    predictor.symptoms,
    format_func=lambda x: predictor.display_name(x),
    placeholder="Example: Fever, Cough, Chest Pain...",
)

symptom_values = {}
if selected:
    cols = st.columns(3)
    for index, symptom in enumerate(selected):
        with cols[index % 3]:
            symptom_values[symptom] = st.slider(predictor.display_name(symptom), 1, 5, 3, key=f"severity_{symptom}")

payload = {
    "age": age, "sex": sex, "pregnancy_status": pregnancy, "smoking_status": smoking,
    "symptom_duration_days": duration, "onset_type": onset, "temperature_c": temperature,
    "heart_rate_bpm": heart_rate, "respiratory_rate_bpm": respiratory_rate,
    "spo2_percent": spo2, "systolic_bp": systolic, "diastolic_bp": diastolic,
    "bmi": bmi, "random_glucose_mg_dl": glucose, "pain_score_0_10": pain,
    "symptoms": symptom_values,
}

if st.button("Analyze symptoms", type="primary", use_container_width=True):
    result = predictor.predict(payload, top_k=5)
    st.session_state["result"] = result

result = st.session_state.get("result")
if result:
    risk = result["risk_assessment"]
    if risk["emergency"]:
        st.error(f"CRITICAL: {risk['urgency']}. " + " | ".join(risk["red_flags"]))
    elif risk["risk_level"] == "High":
        st.error(f"High risk: {risk['urgency']}")
    elif risk["risk_level"] == "Moderate":
        st.warning(f"Moderate risk: {risk['urgency']}")
    else:
        st.success(f"Low risk screen: {risk['urgency']}")

    a, b, c, d = st.columns(4)
    a.metric("Top possibility", result["predictions"][0]["disease_display"])
    b.metric("Model confidence", f"{result['predictions'][0]['probability']:.1%}")
    c.metric("Risk level", risk["risk_level"])
    d.metric("Uncertainty", result["uncertainty"]["status"].title())

    prediction_df = pd.DataFrame([
        {"Possible condition": x["disease_display"], "Probability": x["probability"], "Category": x["category"]}
        for x in result["predictions"]
    ])
    figure = px.bar(prediction_df, x="Probability", y="Possible condition", orientation="h", text_auto=".1%", title="Top differential possibilities")
    figure.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(figure, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Why these results")
        for item in result["predictions"][:3]:
            with st.expander(f"{item['disease_display']} • {item['probability']:.1%}"):
                st.write(f"Category: {item['category']} | Base urgency: {item['base_urgency']}")
                matched = item["explanation"]["matched_signature_symptoms"]
                st.write("Matched signature symptoms:", ", ".join(x["display"] for x in matched) or "None")
                st.write("Missing expected symptoms:", ", ".join(item["explanation"]["missing_signature_symptoms"]) or "None")
        if risk["abnormal_vitals"]:
            st.subheader("Abnormal measurements")
            for item in risk["abnormal_vitals"]:
                st.write("•", item)
    with right:
        st.subheader("Suggested next steps")
        for item in result["care_guidance"]["recommended_actions"]:
            st.write("•", item)
        st.subheader("A clinician may consider")
        for item in result["care_guidance"]["clinician_may_consider"]:
            st.write("•", item)
        st.subheader("Medication safety")
        for item in result["care_guidance"]["medication_safety"]:
            st.write("•", item)

    st.info(result["uncertainty"]["message"])
    st.caption(result["disclaimer"])
    report_col, json_col = st.columns(2)
    with report_col:
        st.download_button("Download PDF report", create_prediction_pdf(result), file_name=f"prediction_{result['prediction_id']}.pdf", mime="application/pdf", use_container_width=True)
    with json_col:
        st.download_button("Download JSON result", json.dumps(result, indent=2), file_name=f"prediction_{result['prediction_id']}.json", mime="application/json", use_container_width=True)

st.divider()
with st.expander("Batch CSV prediction"):
    st.write("Upload up to 200 rows using dataset-style columns. Symptom columns should contain severity values from 0 to 5.")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    if uploaded is not None:
        batch = pd.read_csv(uploaded).head(200)
        if st.button("Run batch prediction"):
            outputs = []
            for _, row in batch.iterrows():
                symptoms = {name: int(row.get(name, 0) or 0) for name in predictor.symptoms if int(row.get(name, 0) or 0) > 0}
                item = {
                    "age": int(row.get("Age", 35)), "sex": str(row.get("Sex", "Other")),
                    "pregnancy_status": str(row.get("Pregnancy_Status", "Not_Applicable")),
                    "smoking_status": str(row.get("Smoking_Status", "Never")),
                    "symptom_duration_days": int(row.get("Symptom_Duration_Days", 1)),
                    "onset_type": str(row.get("Onset_Type", "Gradual")),
                    "temperature_c": float(row.get("Temperature_C", 37.0)),
                    "heart_rate_bpm": int(row.get("Heart_Rate_BPM", 80)),
                    "respiratory_rate_bpm": int(row.get("Respiratory_Rate_BPM", 16)),
                    "spo2_percent": int(row.get("SpO2_Percent", 98)),
                    "systolic_bp": int(row.get("Systolic_BP", 120)),
                    "diastolic_bp": int(row.get("Diastolic_BP", 80)),
                    "bmi": float(row.get("BMI", 23.0)),
                    "random_glucose_mg_dl": int(row.get("Random_Glucose_mg_dL", 100)),
                    "pain_score_0_10": int(row.get("Pain_Score_0_10", 0)),
                    "symptoms": symptoms,
                }
                prediction = predictor.predict(item, top_k=3)
                outputs.append({
                    "Top_Disease": prediction["predictions"][0]["disease"],
                    "Confidence": prediction["predictions"][0]["probability"],
                    "Risk_Level": prediction["risk_assessment"]["risk_level"],
                    "Urgency": prediction["risk_assessment"]["urgency"],
                    "Second_Disease": prediction["predictions"][1]["disease"],
                    "Third_Disease": prediction["predictions"][2]["disease"],
                })
            output_df = pd.concat([batch.reset_index(drop=True), pd.DataFrame(outputs)], axis=1)
            st.dataframe(output_df.head(30), use_container_width=True)
            st.download_button("Download batch results", output_df.to_csv(index=False), "batch_predictions.csv", "text/csv")
