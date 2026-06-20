"""
NCD Shield AI — model training pipeline (tuned).

Trains and compares four classifiers (Random Forest, XGBoost, Logistic
Regression, Decision Tree) with:
  • automatic interaction features (sklearn PolynomialFeatures — stays
    backend-loadable, no custom pickled code),
  • randomized hyperparameter search with stratified cross-validation,
  • class balancing to better catch the minority High-Risk class,
then auto-selects the best by cross-validated weighted F1 and serializes the
winning pipeline + rich metadata with Joblib.

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
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from features import BINARY_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET

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

N_ITER = 10          # randomized-search samples per model
CV_FOLDS = 3
RANDOM_STATE = 42


def build_preprocessor() -> ColumnTransformer:
    """Scale numeric/binary features, add pairwise interactions, OHE categoricals.

    Uses only sklearn-native transformers so the serialized pipeline loads in the
    backend without any custom modules on the path.
    """
    numeric_pipe = Pipeline(
        [
            ("scale", StandardScaler()),
            # interaction_only keeps it to pairwise products (no squared terms),
            # which captures compounding risk factors without exploding dimensionality.
            ("interactions", PolynomialFeatures(degree=2, interaction_only=True,
                                                include_bias=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_FEATURES + BINARY_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def candidate_search_spaces() -> dict:
    """Model + hyperparameter distributions for RandomizedSearchCV.

    Param keys are prefixed `clf__` to target the classifier inside the pipeline.
    """
    spaces = {
        "random_forest": (
            RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1,
                                   class_weight="balanced"),
            {
                "clf__n_estimators": [200, 300, 400],
                "clf__max_depth": [12, 16, 20],
                "clf__min_samples_split": [2, 5, 10],
                "clf__min_samples_leaf": [1, 2, 4],
                "clf__max_features": ["sqrt", "log2"],
            },
        ),
        "logistic_regression": (
            LogisticRegression(max_iter=2000, class_weight="balanced"),
            {
                "clf__C": [0.1, 0.3, 1.0, 3.0, 10.0],
                "clf__solver": ["lbfgs", "saga"],
            },
        ),
        "decision_tree": (
            DecisionTreeClassifier(random_state=RANDOM_STATE, class_weight="balanced"),
            {
                "clf__max_depth": [6, 8, 10, 14, None],
                "clf__min_samples_split": [2, 5, 10, 20],
                "clf__min_samples_leaf": [1, 2, 5],
            },
        ),
    }
    if HAS_XGB:
        spaces["xgboost"] = (
            XGBClassifier(
                objective="multi:softprob", num_class=3, eval_metric="mlogloss",
                random_state=RANDOM_STATE, n_jobs=-1, tree_method="hist",
            ),
            {
                "clf__n_estimators": [200, 300, 400],
                "clf__max_depth": [4, 6, 8],
                "clf__learning_rate": [0.05, 0.08, 0.12],
                "clf__subsample": [0.8, 0.9, 1.0],
                "clf__colsample_bytree": [0.7, 0.85, 1.0],
                "clf__min_child_weight": [1, 3, 5],
                "clf__reg_lambda": [1.0, 2.0, 5.0],
            },
        )
    return spaces


def feature_importance(pipeline: Pipeline) -> dict[str, float]:
    """Extract normalized feature importances from the fitted pipeline."""
    pre: ColumnTransformer = pipeline.named_steps["pre"]
    clf = pipeline.named_steps["clf"]
    try:
        names = pre.get_feature_names_out().tolist()
    except Exception:
        names = []

    if hasattr(clf, "feature_importances_"):
        importances = np.asarray(clf.feature_importances_, dtype=float)
    elif hasattr(clf, "coef_"):
        importances = np.abs(np.asarray(clf.coef_)).mean(axis=0)
    else:
        importances = np.ones(len(names) or 1)

    if not names or len(names) != len(importances):
        names = [f"f{i}" for i in range(len(importances))]

    total = importances.sum() or 1.0
    pairs = sorted(zip(names, importances / total), key=lambda x: x[1], reverse=True)
    # Keep the top 25 — enough for explanations, keeps metadata compact.
    return {name: round(float(val), 4) for name, val in pairs[:25]}


def main() -> None:
    if not os.path.exists(DATA_PATH):
        raise SystemExit(f"Dataset not found at {DATA_PATH}. Run generate_dataset.py first.")

    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    os.makedirs(MODEL_DIR, exist_ok=True)
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    results = {}
    best_name, best_estimator, best_cv_f1 = None, None, -1.0

    print(f"Tuning {('4' if HAS_XGB else '3')} models "
          f"({N_ITER}-sample search × {CV_FOLDS}-fold CV)…\n")

    for name, (clf, space) in candidate_search_spaces().items():
        pipe = Pipeline([("pre", build_preprocessor()), ("clf", clf)])
        search = RandomizedSearchCV(
            pipe, space, n_iter=N_ITER, scoring="f1_weighted", cv=cv,
            n_jobs=-1, random_state=RANDOM_STATE, refit=True,
        )
        search.fit(X_train, y_train)

        cv_f1 = float(search.best_score_)
        preds = search.predict(X_test)
        test_acc = float(accuracy_score(y_test, preds))
        test_f1 = float(f1_score(y_test, preds, average="weighted"))
        test_f1_macro = float(f1_score(y_test, preds, average="macro"))
        results[name] = {
            "cv_f1_weighted": round(cv_f1, 4),
            "accuracy": round(test_acc, 4),
            "f1_weighted": round(test_f1, 4),
            "f1_macro": round(test_f1_macro, 4),
            "best_params": {k.replace("clf__", ""): v for k, v in search.best_params_.items()},
        }
        print(f"  {name:<22} cv_f1={cv_f1:.4f}  test_acc={test_acc:.4f}  "
              f"test_f1={test_f1:.4f}  macro_f1={test_f1_macro:.4f}")

        if cv_f1 > best_cv_f1:
            best_name, best_estimator, best_cv_f1 = name, search.best_estimator_, cv_f1

    final_preds = best_estimator.predict(X_test)
    print(f"\n✅ Best model: {best_name} (cv_f1={best_cv_f1:.4f})\n")
    print(classification_report(y_test, final_preds,
                                target_names=["Low", "Moderate", "High"]))

    joblib.dump(best_estimator, MODEL_PATH)

    metadata = {
        "best_model": best_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(df)),
        "cv_folds": CV_FOLDS,
        "search_iter": N_ITER,
        "comparison": results,
        "best_metrics": results[best_name],
        "best_params": results[best_name]["best_params"],
        "confusion_matrix": confusion_matrix(y_test, final_preds).tolist(),
        "classification_report": classification_report(
            y_test, final_preds, target_names=["Low", "Moderate", "High"],
            output_dict=True),
        "feature_importance": feature_importance(best_estimator),
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
