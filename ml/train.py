"""
NCD Shield AI — model training pipeline.

Trains and compares four classifiers (Random Forest, XGBoost, Logistic Regression,
Decision Tree) on the NCD dataset, automatically selects the best by weighted F1,
and serializes the winning pipeline + metadata with Joblib.

Run:
    python generate_dataset.py   # if dataset not present
    python train.py
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from features import (
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET,
)

try:
    from xgboost import XGBClassifier

    HAS_XGB = True
except Exception:  # pragma: no cover - optional dep
    HAS_XGB = False

HERE = os.path.dirname(__file__)
DATA_PATH = os.path.join(HERE, "data", "ncd_dataset.csv")
MODEL_DIR = os.path.join(HERE, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ncd_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "metadata.json")


def build_preprocessor() -> ColumnTransformer:
    """Scale numeric/binary features and one-hot encode categoricals."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES + BINARY_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def candidate_models() -> dict:
    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=14, n_jobs=-1, random_state=42
        ),
        "logistic_regression": LogisticRegression(max_iter=1000),
        "decision_tree": DecisionTreeClassifier(max_depth=10, random_state=42),
    }
    if HAS_XGB:
        models["xgboost"] = XGBClassifier(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
        )
    return models


def feature_importance(pipeline: Pipeline) -> dict[str, float]:
    """Extract normalized feature importances from the fitted pipeline."""
    pre: ColumnTransformer = pipeline.named_steps["pre"]
    clf = pipeline.named_steps["clf"]
    try:
        names = pre.get_feature_names_out().tolist()
    except Exception:
        names = NUMERIC_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES

    if hasattr(clf, "feature_importances_"):
        importances = np.asarray(clf.feature_importances_, dtype=float)
    elif hasattr(clf, "coef_"):
        importances = np.abs(np.asarray(clf.coef_)).mean(axis=0)
    else:
        importances = np.ones(len(names))

    importances = importances[: len(names)]
    total = importances.sum() or 1.0
    pairs = sorted(zip(names, importances / total), key=lambda x: x[1], reverse=True)
    return {name: round(float(val), 4) for name, val in pairs}


def main() -> None:
    if not os.path.exists(DATA_PATH):
        raise SystemExit(f"Dataset not found at {DATA_PATH}. Run generate_dataset.py first.")

    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    os.makedirs(MODEL_DIR, exist_ok=True)
    results = {}
    best_name, best_pipeline, best_f1 = None, None, -1.0

    for name, clf in candidate_models().items():
        pipe = Pipeline([("pre", build_preprocessor()), ("clf", clf)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")
        results[name] = {"accuracy": round(float(acc), 4), "f1_weighted": round(float(f1), 4)}
        print(f"  {name:<22} acc={acc:.4f}  f1={f1:.4f}")
        if f1 > best_f1:
            best_name, best_pipeline, best_f1 = name, pipe, f1

    print(f"\n✅ Best model: {best_name} (f1={best_f1:.4f})\n")
    print(classification_report(y_test, best_pipeline.predict(X_test)))

    joblib.dump(best_pipeline, MODEL_PATH)

    metadata = {
        "best_model": best_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(df)),
        "comparison": results,
        "best_metrics": results[best_name],
        "feature_importance": feature_importance(best_pipeline),
        "numeric_features": NUMERIC_FEATURES,
        "binary_features": BINARY_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
    }
    with open(META_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved model  -> {MODEL_PATH}")
    print(f"Saved meta   -> {META_PATH}")


if __name__ == "__main__":
    main()
