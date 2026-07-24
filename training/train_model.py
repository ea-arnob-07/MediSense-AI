from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import softmax
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    top_k_accuracy_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, normalize

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "disease_prediction_dataset_expanded.csv"
SYMPTOM_PATH = ROOT / "data" / "symptom_dictionary.csv"
PROFILE_PATH = ROOT / "data" / "disease_profiles.csv"
ARTIFACT_DIR = ROOT / "artifacts"
ARTIFACT_DIR.mkdir(exist_ok=True)

LEAKAGE_COLUMNS = {
    "Case_ID", "Data_Origin", "Split", "Disease", "Disease_Severity",
    "Disease_Category", "Emergency_Red_Flag", "Urgency_Level",
    "Symptom_Count", "Max_Symptom_Severity", "Mean_Present_Severity",
}


def expected_calibration_error(y_true: pd.Series, probabilities: np.ndarray, classes: np.ndarray, bins: int = 15) -> float:
    mapping = {label: i for i, label in enumerate(classes)}
    true_index = np.array([mapping[x] for x in y_true])
    confidence = probabilities.max(axis=1)
    correct = probabilities.argmax(axis=1) == true_index
    edges = np.linspace(0, 1, bins + 1)
    value = 0.0
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (confidence > lower) & (confidence <= upper)
        if mask.any():
            value += mask.mean() * abs(correct[mask].mean() - confidence[mask].mean())
    return float(value)


def evaluate(y_true: pd.Series, probabilities: np.ndarray, classes: np.ndarray) -> tuple[dict, np.ndarray]:
    predictions = classes[probabilities.argmax(axis=1)]
    metrics = {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "macro_f1": float(f1_score(y_true, predictions, average="macro")),
        "weighted_f1": float(f1_score(y_true, predictions, average="weighted")),
        "top3_accuracy": float(top_k_accuracy_score(y_true, probabilities, k=3, labels=classes)),
        "top5_accuracy": float(top_k_accuracy_score(y_true, probabilities, k=5, labels=classes)),
        "log_loss": float(log_loss(y_true, probabilities, labels=classes)),
        "expected_calibration_error": expected_calibration_error(y_true, probabilities, classes),
        "mean_confidence": float(probabilities.max(axis=1).mean()),
    }
    return metrics, predictions


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    symptom_df = pd.read_csv(SYMPTOM_PATH)
    profile_df = pd.read_csv(PROFILE_PATH).fillna("")
    symptoms = symptom_df["Symptom"].tolist()
    features = [column for column in data.columns if column not in LEAKAGE_COLUMNS]
    categorical = [column for column in features if data[column].dtype == "object"]
    continuous = [column for column in features if column not in categorical and column not in symptoms]

    train = data[data["Split"] == "Train"].copy()
    validation = data[data["Split"] == "Validation"].copy()
    test = data[data["Split"] == "Test"].copy()

    preprocessor = ColumnTransformer([
        ("symptoms", SimpleImputer(strategy="constant", fill_value=0), symptoms),
        ("continuous", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", MinMaxScaler(feature_range=(0, 5))),
        ]), continuous),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical),
    ], sparse_threshold=1.0, verbose_feature_names_out=False)

    pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("classifier", MultinomialNB(alpha=0.2)),
    ])
    pipeline.fit(train[features], train["Disease"])
    classes = pipeline.classes_

    x_train_symptoms = train[symptoms].to_numpy(dtype=np.float32)
    class_means = np.stack([
        x_train_symptoms[train["Disease"].to_numpy() == disease].mean(axis=0)
        for disease in classes
    ])
    idf = np.log((1 + len(x_train_symptoms)) / (1 + (x_train_symptoms > 0).sum(axis=0))) + 1
    weighted_prototypes = normalize(class_means * np.sqrt(idf))

    def components(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        nb_probability = pipeline.predict_proba(frame[features])
        x = frame[symptoms].to_numpy(dtype=np.float32)
        prototype_score = normalize(x * np.sqrt(idf)) @ weighted_prototypes.T
        return nb_probability, prototype_score

    validation_nb, validation_score = components(validation)
    best = None
    for prototype_temperature in [0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.07, 0.10, 0.15]:
        prototype_probability = softmax(validation_score / prototype_temperature, axis=1)
        for nb_weight in np.arange(0.50, 1.001, 0.05):
            combined = np.clip(nb_weight * validation_nb + (1 - nb_weight) * prototype_probability, 1e-12, 1)
            accuracy = accuracy_score(validation["Disease"], classes[combined.argmax(axis=1)])
            loss = log_loss(validation["Disease"], combined, labels=classes)
            candidate = ((accuracy, -loss), prototype_temperature, float(nb_weight), combined)
            if best is None or candidate[0] > best[0]:
                best = candidate

    _, prototype_temperature, nb_weight, validation_combined = best
    class_index = {label: i for i, label in enumerate(classes)}
    validation_true_index = np.array([class_index[x] for x in validation["Disease"]])
    validation_log_probability = np.log(np.clip(validation_combined, 1e-12, 1))

    def temperature_loss(value: float) -> float:
        probability = softmax(validation_log_probability / value, axis=1)
        return float(-np.mean(np.log(np.clip(probability[np.arange(len(probability)), validation_true_index], 1e-12, 1))))

    calibration_temperature = float(minimize_scalar(temperature_loss, bounds=(0.5, 3.0), method="bounded").x)

    def final_probability(frame: pd.DataFrame) -> np.ndarray:
        nb_probability, prototype_score = components(frame)
        prototype_probability = softmax(prototype_score / prototype_temperature, axis=1)
        combined = np.clip(nb_weight * nb_probability + (1 - nb_weight) * prototype_probability, 1e-12, 1)
        return softmax(np.log(combined) / calibration_temperature, axis=1)

    validation_probability = final_probability(validation)
    test_probability = final_probability(test)
    validation_metrics, _ = evaluate(validation["Disease"], validation_probability, classes)
    test_metrics, test_predictions = evaluate(test["Disease"], test_probability, classes)

    report = pd.DataFrame(classification_report(test["Disease"], test_predictions, output_dict=True, zero_division=0)).T
    report.to_csv(ARTIFACT_DIR / "classification_report.csv")
    pd.DataFrame(confusion_matrix(test["Disease"], test_predictions, labels=classes), index=classes, columns=classes).to_csv(ARTIFACT_DIR / "confusion_matrix.csv")

    defaults = {}
    for feature in features:
        if feature in symptoms:
            defaults[feature] = 0
        elif data[feature].dtype == "object":
            mode = train[feature].mode(dropna=True)
            defaults[feature] = mode.iloc[0] if not mode.empty else "Unknown"
        else:
            defaults[feature] = float(train[feature].median())

    input_options = {}
    for feature in categorical:
        input_options[feature] = sorted(str(x) for x in data[feature].dropna().unique())

    profiles = {row["Disease"]: row.to_dict() for _, row in profile_df.iterrows()}
    symptom_metadata = {row["Symptom"]: row.to_dict() for _, row in symptom_df.fillna("").iterrows()}
    baseline = {
        "symptom_prevalence": {symptom: float((train[symptom] > 0).mean()) for symptom in symptoms},
        "continuous_quantiles": {
            feature: {str(q): float(train[feature].quantile(q)) for q in [0.05, 0.25, 0.5, 0.75, 0.95]}
            for feature in continuous
        },
    }

    model_version = datetime.now(UTC).strftime("synthetic-ensemble-%Y%m%d-%H%M%S")
    artifact = {
        "pipeline": pipeline,
        "classes": classes,
        "symptoms": symptoms,
        "features": features,
        "categorical_features": categorical,
        "continuous_features": continuous,
        "prototype_means_weighted": weighted_prototypes,
        "prototype_idf": idf,
        "prototype_temperature": prototype_temperature,
        "nb_weight": nb_weight,
        "calibration_temperature": calibration_temperature,
        "disease_profiles": profiles,
        "symptom_metadata": symptom_metadata,
        "defaults": defaults,
        "input_options": input_options,
        "training_baseline": baseline,
        "metrics": {"validation": validation_metrics, "test": test_metrics},
        "model_version": model_version,
        "training_notes": {
            "dataset_rows": len(data),
            "train_rows": len(train),
            "validation_rows": len(validation),
            "test_rows": len(test),
            "diseases": len(classes),
            "symptoms": len(symptoms),
            "synthetic_dataset": True,
        },
    }
    joblib.dump(artifact, ARTIFACT_DIR / "disease_ensemble.joblib", compress=3)

    metadata = {
        "model_version": model_version,
        "selected_parameters": {
            "multinomial_nb_alpha": 0.2,
            "nb_weight": nb_weight,
            "prototype_weight": 1 - nb_weight,
            "prototype_temperature": prototype_temperature,
            "calibration_temperature": calibration_temperature,
        },
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "data": artifact["training_notes"],
        "excluded_leakage_columns": sorted(LEAKAGE_COLUMNS),
    }
    (ARTIFACT_DIR / "model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Evaluation chart
    labels = ["Top-1", "Top-3", "Top-5", "Macro F1"]
    values = [test_metrics["accuracy"], test_metrics["top3_accuracy"], test_metrics["top5_accuracy"], test_metrics["macro_f1"]]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)
    plt.ylim(0, 1.05)
    plt.ylabel("Score")
    plt.title("Held-out Test Performance")
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.012, f"{value:.3f}", ha="center")
    plt.tight_layout()
    plt.savefig(ARTIFACT_DIR / "test_performance.png", dpi=180)
    plt.close()

    # Reliability plot
    confidence = test_probability.max(axis=1)
    true_index = np.array([class_index[x] for x in test["Disease"]])
    correct = test_probability.argmax(axis=1) == true_index
    bin_edges = np.linspace(0, 1, 11)
    x_values, y_values = [], []
    for lower, upper in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (confidence > lower) & (confidence <= upper)
        if mask.any():
            x_values.append(float(confidence[mask].mean()))
            y_values.append(float(correct[mask].mean()))
    plt.figure(figsize=(6, 6))
    plt.plot([0, 1], [0, 1], linestyle="--", label="Perfect calibration")
    plt.plot(x_values, y_values, marker="o", label="Model")
    plt.xlabel("Mean confidence")
    plt.ylabel("Observed accuracy")
    plt.title("Reliability Diagram")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ARTIFACT_DIR / "reliability_diagram.png", dpi=180)
    plt.close()

    # F1 by support
    class_rows = report.loc[[x for x in classes if x in report.index]].copy()
    plt.figure(figsize=(8, 5))
    plt.scatter(class_rows["support"], class_rows["f1-score"], alpha=0.65)
    plt.xlabel("Test examples per disease")
    plt.ylabel("F1 score")
    plt.title("Class Support vs F1")
    plt.tight_layout()
    plt.savefig(ARTIFACT_DIR / "support_vs_f1.png", dpi=180)
    plt.close()

    # Top discriminative features for Naive Bayes
    feature_names = pipeline.named_steps["preprocess"].get_feature_names_out()
    feature_log_probability = pipeline.named_steps["classifier"].feature_log_prob_
    discriminative = feature_log_probability.std(axis=0)
    top = np.argsort(discriminative)[-30:][::-1]
    plt.figure(figsize=(10, 8))
    plt.barh([str(feature_names[i]) for i in top][::-1], discriminative[top][::-1])
    plt.xlabel("Across-disease log-probability variation")
    plt.title("Most Discriminative Model Features")
    plt.tight_layout()
    plt.savefig(ARTIFACT_DIR / "top_model_features.png", dpi=180)
    plt.close()

    model_card = f"""# Model Card\n\n## Intended use\nEducational disease-prediction and triage demonstration. It ranks possible conditions and highlights warning signs. It must not be used for autonomous diagnosis, treatment, medication decisions, emergency dispatch, or clinical care without professional validation and oversight.\n\n## Data\n- Synthetic, medically informed dataset\n- Rows: {len(data):,}\n- Diseases: {len(classes)}\n- Symptoms: {len(symptoms)}\n- Severity scale: 0–5\n\n## Model\nEnsemble of calibrated Multinomial Naive Bayes and severity-profile cosine similarity. A deterministic safety layer separately evaluates emergency warning signs and abnormal measurements.\n\n## Held-out test results\n- Top-1 accuracy: {test_metrics['accuracy']:.4f}\n- Macro F1: {test_metrics['macro_f1']:.4f}\n- Top-3 accuracy: {test_metrics['top3_accuracy']:.4f}\n- Top-5 accuracy: {test_metrics['top5_accuracy']:.4f}\n- Log loss: {test_metrics['log_loss']:.4f}\n- Expected calibration error: {test_metrics['expected_calibration_error']:.4f}\n\nThese numbers measure fit to this synthetic dataset, not safety or accuracy in real patients.\n\n## Key limitations\n- The dataset does not represent a clinical population or verified diagnoses.\n- Real symptoms may be incomplete, ambiguous, culturally described, or affected by comorbidities and medicines.\n- Disease prevalence and severity differ by geography, age, season, and healthcare setting.\n- A high probability is not proof of disease. A low probability does not rule it out.\n- The triage thresholds are conservative educational heuristics, not a validated triage protocol.\n\n## Safety references\n- MedlinePlus, recognizing medical emergencies: https://medlineplus.gov/ency/article/001927.htm\n- CDC, stroke signs and symptoms: https://www.cdc.gov/stroke/signs-symptoms/index.html\n- WHO, dengue warning signs: https://www.who.int/news-room/questions-and-answers/item/dengue-and-severe-dengue\n- NHS, heart attack emergency symptoms: https://www.nhs.uk/conditions/heart-attack/\n"""
    (ARTIFACT_DIR / "MODEL_CARD.md").write_text(model_card, encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
