"""
train_and_test_tn_v4.py

- Loads: TamilNadu_Water_Quality_Synthetic_V2.csv
- Preprocess: median imputation (if needed), StandardScaler
- Model: RandomForest inside a Pipeline
- Evaluation: classification report, confusion matrix, ROC/AUC
- Robustness test: evaluate with added sensor noise (±5%)
- Saves model pipeline as: tamilnadu_water_model_v4.joblib
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import joblib

RANDOM_STATE = 42
CSV_FILE = "TamilNadu_Water_Quality_Synthetic_V2.csv"
OUTPUT_MODEL = "tamilnadu_water_model_v4.joblib"

def load_data(path):
    df = pd.read_csv(path)
    print("Dataset Loaded! Shape:", df.shape)
    print(df.head())
    return df

def build_pipeline():
    """Create preprocessing + model pipeline"""
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),   # handles any accidental NaNs
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=400,
            max_depth=20,
            class_weight="balanced",
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])
    return pipeline

def plot_confusion_matrix(cm, classes, title="Confusion matrix", cmap=plt.cm.Blues, out="confusion_matrix.png"):
    plt.figure(figsize=(5,4))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes)
    plt.yticks(tick_marks, classes)
    thresh = cm.max() / 2.
    for i, j in np.ndindex(cm.shape):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black",
                 fontsize=14)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def plot_roc(y_true, y_score, out="roc_curve.png"):
    fpr, tpr, _ = roc_curve(y_true, y_score)
    auc = roc_auc_score(y_true, y_score)
    plt.figure(figsize=(6,5))
    plt.plot(fpr, tpr, linewidth=2)
    plt.plot([0,1], [0,1], linestyle='--', color='grey')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC curve (AUC = {auc:.3f})")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def evaluate_model(pipe, X_test, y_test):
    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else None

    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:\n", cm)
    plot_confusion_matrix(cm, classes=["Unsafe(0)","Safe(1)"], out="confusion_matrix_v4.png")

    if y_proba is not None:
        print("ROC AUC:", roc_auc_score(y_test, y_proba))
        plot_roc(y_test, y_proba, out="roc_v4.png")
    return acc, cm

def robustness_test(pipe, X_test, y_test, noise_level=0.05, trials=5):
    """Add random multiplicative noise (±noise_level) and evaluate"""
    print(f"\n--- Robustness test: noise ±{noise_level*100:.1f}% ---")
    accs = []
    for t in range(trials):
        X_noisy = X_test.copy().astype(float)
        noise = np.random.uniform(-noise_level, noise_level, X_noisy.shape)
        X_noisy = X_noisy * (1 + noise)
        y_pred = pipe.predict(X_noisy)
        acc = accuracy_score(y_test, y_pred)
        accs.append(acc)
        print(f"Trial {t+1}: accuracy = {acc:.4f}")
    print("Robustness summary: mean =", np.mean(accs), "std =", np.std(accs))
    return accs

def main():
    # Check for either V2 or original CSV
    csv_file = CSV_FILE
    if not os.path.exists(csv_file):
        # Fallback to existing file if V2 not found, or user might want to use existing one
        # The user prompt mentioned "TamilNadu_Water_Quality_Synthetic_V2.csv" but the file list showed "TamilNadu_Water_Quality.csv"
        # I will check for the one present in the directory.
        if os.path.exists("TamilNadu_Water_Quality.csv"):
             csv_file = "TamilNadu_Water_Quality.csv"
             print(f"Using existing dataset: {csv_file}")
        else:
             raise FileNotFoundError(f"CSV file not found: {CSV_FILE} or TamilNadu_Water_Quality.csv")

    # Load
    df = load_data(csv_file)

    # Features and label
    # The user's code expects "Potability" but the existing dataset might have "is_safe" or similar.
    # Let's check columns.
    if "Potability" not in df.columns:
        if "is_safe" in df.columns:
             print("Renaming 'is_safe' to 'Potability' for compatibility")
             df["Potability"] = df["is_safe"]
             df = df.drop("is_safe", axis=1)
        else:
             # If neither, we might have a problem, but let's assume one exists based on previous file content
             pass

    if "Potability" not in df.columns:
        raise KeyError("Expected column 'Potability' (or 'is_safe') not found in CSV.")
        
    X = df.drop("Potability", axis=1)
    y = df["Potability"].astype(int)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    print("\nTraining Samples:", X_train.shape[0], " Testing Samples:", X_test.shape[0])

    # Build pipeline
    pipe = build_pipeline()

    # Cross-validated score (quick)
    print("\nCross-validating (5-fold) on training set ...")
    cv_scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="accuracy", n_jobs=-1)
    print("CV accuracy scores:", np.round(cv_scores, 4))
    print("CV mean accuracy:", np.round(cv_scores.mean(), 4))

    # Fit
    print("\nTraining final model ...")
    pipe.fit(X_train, y_train)

    # Evaluate
    print("\n--- Test set evaluation ---")
    evaluate_model(pipe, X_test, y_test)

    # Robustness
    robustness_test(pipe, X_test, y_test, noise_level=0.05, trials=5)

    # Feature importances (from RF)
    if hasattr(pipe.named_steps['rf'], "feature_importances_"):
        importances = pipe.named_steps['rf'].feature_importances_
        feature_names = X.columns
        plt.figure(figsize=(8,5))
        plt.barh(feature_names, importances)
        plt.xlabel("Importance")
        plt.title("Feature Importance - tamilnadu_water_model_v4")
        plt.tight_layout()
        plt.savefig("feature_importance_v4.png")
        plt.close()
        print("\nFeature importance saved as feature_importance_v4.png")

    # Save model
    joblib.dump(pipe, OUTPUT_MODEL)
    print(f"\n✅ Model pipeline saved to: {OUTPUT_MODEL}")

    # Optional: show a quick sample prediction (with probabilities)
    sample = X_test.iloc[:5].copy()
    print("\nSample predictions (first 5 test rows):")
    print(sample)
    preds = pipe.predict(sample)
    probs = pipe.predict_proba(sample)[:,1] if hasattr(pipe, "predict_proba") else None
    for i, p in enumerate(preds):
        if probs is not None:
            print(f"Row {i}: pred={p}  prob_safe={probs[i]:.3f}")
        else:
            print(f"Row {i}: pred={p}")

if __name__ == "__main__":
    main()
