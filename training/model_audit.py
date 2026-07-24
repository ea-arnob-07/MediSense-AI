from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import softmax
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import normalize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "disease_prediction_dataset_expanded.csv"
MODEL = ROOT / "artifacts" / "disease_ensemble.joblib"
OUT = ROOT / "artifacts"


def predict_probabilities(frame: pd.DataFrame, artifact: dict) -> np.ndarray:
    pipeline = artifact["pipeline"]
    features = artifact["features"]
    symptoms = artifact["symptoms"]
    nb_probability = pipeline.predict_proba(frame[features])
    x = frame[symptoms].to_numpy(dtype=np.float32)
    idf = np.asarray(artifact["prototype_idf"], dtype=np.float32)
    prototypes = np.asarray(artifact["prototype_means_weighted"], dtype=np.float32)
    prototype_score = normalize(x * np.sqrt(idf)) @ prototypes.T
    prototype_probability = softmax(prototype_score / artifact["prototype_temperature"], axis=1)
    combined = np.clip(
        artifact["nb_weight"] * nb_probability + (1 - artifact["nb_weight"]) * prototype_probability,
        1e-12,
        1,
    )
    return softmax(np.log(combined) / artifact["calibration_temperature"], axis=1)


def metric_row(name: str, value: str, y_true: pd.Series, y_pred: np.ndarray) -> dict:
    return {
        "slice": name,
        "value": value,
        "records": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def main() -> None:
    df = pd.read_csv(DATA)
    artifact = joblib.load(MODEL)
    test = df[df["Split"] == "Test"].copy()
    probabilities = predict_probabilities(test, artifact)
    predictions = artifact["classes"][probabilities.argmax(axis=1)]
    test["Predicted_Disease"] = predictions
    test["Confidence"] = probabilities.max(axis=1)

    # Subgroup and slice metrics
    test["Age_Group"] = pd.cut(test["Age"], bins=[-1, 17, 39, 59, 200], labels=["0-17", "18-39", "40-59", "60+"])
    profile_category = {name: profile.get("Category", "Other") for name, profile in artifact["disease_profiles"].items()}
    test["True_Category"] = test["Disease"].map(profile_category)
    rows = []
    for column in ["Sex", "Age_Group", "Pregnancy_Status", "Smoking_Status", "True_Category"]:
        for value, group in test.groupby(column, observed=True):
            if len(group) < 20:
                continue
            rows.append(metric_row(column, str(value), group["Disease"], group["Predicted_Disease"].to_numpy()))
    subgroup = pd.DataFrame(rows).sort_values(["slice", "records"], ascending=[True, False])
    subgroup.to_csv(OUT / "subgroup_metrics.csv", index=False)

    # Most frequent confusions
    errors = test[test["Disease"] != test["Predicted_Disease"]]
    confusions = (
        errors.groupby(["Disease", "Predicted_Disease"], observed=True)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    confusions.to_csv(OUT / "top_confusions.csv", index=False)

    # Data-quality audit
    symptoms = artifact["symptoms"]
    invalid_symptoms = {
        symptom: int(((df[symptom] < 0) | (df[symptom] > 5) | (df[symptom] % 1 != 0)).sum())
        for symptom in symptoms
    }
    data_quality = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_case_ids": int(df["Case_ID"].duplicated().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_by_column": {k: int(v) for k, v in df.isna().sum().sort_values(ascending=False).head(20).items()},
        "invalid_symptom_values_total": int(sum(invalid_symptoms.values())),
        "invalid_symptom_columns": {k: v for k, v in invalid_symptoms.items() if v},
        "disease_classes": int(df["Disease"].nunique()),
        "minimum_class_rows": int(df["Disease"].value_counts().min()),
        "maximum_class_rows": int(df["Disease"].value_counts().max()),
        "split_counts": {k: int(v) for k, v in df["Split"].value_counts().items()},
        "warning": "Passing structural checks does not make synthetic data clinically representative.",
    }
    (OUT / "data_quality_report.json").write_text(json.dumps(data_quality, indent=2), encoding="utf-8")

    # Feature schema for integrations
    schema = {
        "severity_scale": {"minimum": 0, "maximum": 5, "meaning": {"0": "absent", "1": "very mild", "2": "mild", "3": "moderate", "4": "severe", "5": "very severe/critical"}},
        "symptoms": symptoms,
        "continuous_features": artifact["continuous_features"],
        "categorical_features": artifact["categorical_features"],
        "input_options": artifact["input_options"],
        "target": "Disease",
        "excluded_training_columns": ["Case_ID", "Data_Origin", "Split", "Disease_Severity", "Disease_Category", "Emergency_Red_Flag", "Urgency_Level", "Symptom_Count", "Max_Symptom_Severity", "Mean_Present_Severity"],
    }
    (OUT / "feature_schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    # Slice-performance visualization
    plot_df = subgroup[subgroup["slice"].isin(["Sex", "Age_Group", "True_Category"])].copy()
    plot_df["label"] = plot_df["slice"] + ": " + plot_df["value"]
    plot_df = plot_df.sort_values("accuracy").tail(30)
    plt.figure(figsize=(10, 9))
    plt.barh(plot_df["label"], plot_df["accuracy"])
    plt.xlim(0, 1.02)
    plt.xlabel("Accuracy")
    plt.title("Selected Subgroup and Disease-Category Performance")
    plt.tight_layout()
    plt.savefig(OUT / "subgroup_performance.png", dpi=180)
    plt.close()

    print(f"Saved {len(subgroup)} subgroup rows and {len(confusions)} confusion pairs")


if __name__ == "__main__":
    main()
