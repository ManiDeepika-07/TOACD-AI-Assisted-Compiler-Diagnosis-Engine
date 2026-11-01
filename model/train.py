"""
model/train.py
Gradient Boosting training pipeline.

Model: sklearn GradientBoostingClassifier (robust, fast, no extra deps).
Features: 35 structured AST/stderr features + TF-IDF source tokens (top 200).
Output: models/error_classifier.pkl, models/tfidf_vectorizer.pkl,
        models/feature_columns.pkl, models/auxiliary_classifiers.pkl
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)

DATA_CSV   = os.path.join(_SCRIPT_DIR, "data", "features.csv")
MODEL_DIR  = os.path.join(_SCRIPT_DIR, "models")


# ──────────────────────────────────────────────────────────────────────────────
#  Severity / category / nature override rules (deterministic for high-conf)
# ──────────────────────────────────────────────────────────────────────────────
OVERRIDE_LABELS = {
    "no_error":               ("Low",      "N/A",          "N/A"),
    "missing_semicolon":      ("Low",      "Compile-time", "Syntax"),
    "missing_brace":          ("Medium",   "Compile-time", "Syntax"),
    "undeclared_variable":    ("High",     "Compile-time", "Syntax"),
    "uninitialized_variable": ("Medium",   "Runtime",      "Logical"),
    "type_mismatch":          ("Medium",   "Compile-time", "Syntax"),
    "division_by_zero":       ("High",     "Runtime",      "Logical"),
    "null_ptr_access":        ("High",     "Runtime",      "Logical"),
    "infinite_loop":          ("High",     "Runtime",      "Logical"),
    "assignment_in_condition": ("Medium",  "Runtime",      "Logical"),
    "out_of_bounds":          ("High",     "Runtime",      "Logical"),
    "buffer_overflow":        ("Critical", "Runtime",      "Security"),
    "use_after_free":         ("Critical", "Runtime",      "Security"),
    "command_injection":      ("Critical", "Runtime",      "Security"),
    "format_string":          ("Critical", "Runtime",      "Security"),
    "integer_overflow":       ("High",     "Runtime",      "Security"),
    "multi_error":            ("High",     "Runtime",      "Logical"),
}


# ──────────────────────────────────────────────────────────────────────────────
#  Training
# ──────────────────────────────────────────────────────────────────────────────

def train(data_csv: str = DATA_CSV, model_dir: str = MODEL_DIR):
    print(f"\n{'=' * 60}")
    print("  CD 2.0 — Model Training Pipeline")
    print(f"{'=' * 60}")

    if not os.path.exists(data_csv):
        print(f"[ERROR] Features CSV not found: {data_csv}")
        print("Run: python dataset/processor.py")
        return

    df = pd.read_csv(data_csv, keep_default_na=False)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Class distribution:\n{df['error_type'].value_counts()}\n")

    # ── Feature matrix ───────────────────────────────────────────────────────
    label_cols = ["file", "error_type", "severity", "category", "nature"]
    feature_cols = [c for c in df.columns if c not in label_cols]

    X = df[feature_cols].astype(float)
    y_type = df["error_type"]
    y_sev  = df["severity"]
    y_cat  = df["category"]
    y_nat  = df["nature"]

    print(f"Feature count: {len(feature_cols)}")

    # ── Train / test split ────────────────────────────────────────────────────
    X_tr, X_te, yt_tr, yt_te = train_test_split(
        X, y_type, test_size=0.2, random_state=42, stratify=y_type
    )
    _, _, ys_tr, ys_te = train_test_split(X, y_sev,  test_size=0.2, random_state=42)
    _, _, yc_tr, yc_te = train_test_split(X, y_cat,  test_size=0.2, random_state=42)
    _, _, yn_tr, yn_te = train_test_split(X, y_nat,  test_size=0.2, random_state=42)

    # ── Primary model: Gradient Boosting ─────────────────────────────────────
    print("Training primary GradientBoostingClassifier (error_type)…")
    model_type = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.8,
        random_state=42,
        verbose=0,
    )
    model_type.fit(X_tr, yt_tr)
    y_pred = model_type.predict(X_te)
    print(f"\nError Type Accuracy: {accuracy_score(yt_te, y_pred):.4f}")
    print(classification_report(yt_te, y_pred, zero_division=0))

    # ── Auxiliary models: RandomForest (fast, good for small sub-tasks) ──────
    print("Training auxiliary classifiers (severity / category / nature)…")
    model_sev = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
    model_sev.fit(X_tr, ys_tr)

    model_cat = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
    model_cat.fit(X_tr, yc_tr)

    model_nat = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
    model_nat.fit(X_tr, yn_tr)

    print(f"Severity Accuracy: {accuracy_score(ys_te, model_sev.predict(X_te)):.4f}")
    print(f"Category Accuracy: {accuracy_score(yc_te, model_cat.predict(X_te)):.4f}")
    print(f"Nature   Accuracy: {accuracy_score(yn_te, model_nat.predict(X_te)):.4f}")

    # ── Save models ───────────────────────────────────────────────────────────
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model_type,   os.path.join(model_dir, "error_classifier.pkl"))
    joblib.dump(model_sev,    os.path.join(model_dir, "severity_classifier.pkl"))
    joblib.dump(model_cat,    os.path.join(model_dir, "category_classifier.pkl"))
    joblib.dump(model_nat,    os.path.join(model_dir, "nature_classifier.pkl"))
    joblib.dump(feature_cols, os.path.join(model_dir, "feature_columns.pkl"))
    joblib.dump(OVERRIDE_LABELS, os.path.join(model_dir, "override_labels.pkl"))

    print(f"\nModels saved to {model_dir}/")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    train()
