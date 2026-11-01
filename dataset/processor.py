"""
dataset/processor.py
Feature extractor: processes generated .cpp files → features.csv
Works both with Clang (full features) and without (regex-only features).
"""

import os
import sys
import json
import re
import pandas as pd

# Make parser importable
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)

from parser.clang_parser import run_clang, extract_stderr_features, extract_ast_features


# ──────────────────────────────────────────────────────────────────────────────
#  Feature extraction helpers
# ──────────────────────────────────────────────────────────────────────────────

def _regex_only_features(source_text: str) -> dict:
    """Fallback features extracted purely from source text (no Clang)."""
    t = source_text.lower()
    return {
        "total_nodes": 0, "depth_max": 0, "uninit_vars": 0, "null_ptrs": 0,
        "has_while_true":       int(bool(re.search(r"while\s*\(\s*(true|1)\s*\)", source_text))),
        "loop_without_exit":    0,
        "loop_exit_count":      len(re.findall(r"\b(break|return|exit)\s*[\(;]", source_text)),
        "implicit_cast_count":  0,
        "cstyle_cast_count":    len(re.findall(r"\([a-zA-Z_]\w*\s*\*?\)", source_text)),
        "reinterpret_cast_count":len(re.findall(r"reinterpret_cast", source_text)),
        "strcpy_call":          int("strcpy" in t),
        "gets_call":            int("gets(" in t),
        "sprintf_call":         int("sprintf(" in t),
        "system_call":          int("system(" in t),
        "malloc_call":          int("malloc(" in t),
        "free_call":            int("free(" in t),
        "printf_userctrl":      int(bool(re.search(r"printf\s*\(\s*[^\"']", source_text))),
        # stderr flags all zero (no Clang)
        "stderr_has_error": 0, "stderr_has_warning": 0,
        "stderr_error_count": 0, "stderr_warning_count": 0,
        "stderr_missing_brace": 0, "stderr_missing_semi": 0,
        "stderr_expected_expr": 0, "stderr_undeclared": 0,
        "stderr_type_mismatch": 0, "stderr_implicit_narrowing": 0,
        "stderr_void_return": 0, "stderr_return_type": 0,
        "stderr_null_deref": 0, "stderr_uninit": 0, "stderr_div_zero": 0,
        "stderr_deprecated": 0, "stderr_format_security": 0, "stderr_buffer": 0,
        "node_counts": {},
    }


def extract_features_for_file(file_path: str) -> dict:
    """
    Full feature extraction for one .cpp file.
    Falls back to regex-only if Clang is unavailable.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            source_text = fh.read()
    except Exception:
        source_text = ""

    ast_text, stderr_text = run_clang(file_path)
    clang_available = bool(ast_text or stderr_text)

    if clang_available:
        ast_feats    = extract_ast_features(ast_text, source_text)
        stderr_feats = extract_stderr_features(stderr_text)
        features = {**ast_feats, **stderr_feats}
    else:
        features = _regex_only_features(source_text)

    features["_source"] = source_text   # kept for TF-IDF later
    return features


# ──────────────────────────────────────────────────────────────────────────────
#  Main processor
# ──────────────────────────────────────────────────────────────────────────────

# Fixed scalar columns (always present)
_SCALAR_COLS = [
    "total_nodes", "depth_max", "uninit_vars", "null_ptrs",
    "has_while_true", "loop_without_exit", "loop_exit_count",
    "implicit_cast_count", "cstyle_cast_count", "reinterpret_cast_count",
    "strcpy_call", "gets_call", "sprintf_call", "system_call",
    "malloc_call", "free_call", "printf_userctrl",
    "stderr_has_error", "stderr_has_warning",
    "stderr_error_count", "stderr_warning_count",
    "stderr_missing_brace", "stderr_missing_semi", "stderr_expected_expr",
    "stderr_undeclared", "stderr_type_mismatch", "stderr_implicit_narrowing",
    "stderr_void_return", "stderr_return_type", "stderr_null_deref",
    "stderr_uninit", "stderr_div_zero", "stderr_deprecated",
    "stderr_format_security", "stderr_buffer",
]


def process_dataset(dataset_dir: str = "data/dataset", out_csv: str = "data/features.csv"):
    labels_path = os.path.join(dataset_dir, "labels.json")
    if not os.path.exists(labels_path):
        print("Labels file not found! Run dataset/generator.py first.")
        return

    with open(labels_path, "r") as fh:
        labels_data = json.load(fh)

    records = []
    for idx, entry in enumerate(labels_data):
        file_path = os.path.join(dataset_dir, entry["file"])
        if not os.path.exists(file_path):
            continue

        features = extract_features_for_file(file_path)
        source   = features.pop("_source", "")

        row = {
            "file":       entry["file"],
            "error_type": entry["error_type"],
            "severity":   entry["severity"],
            "category":   entry["category"],
            "nature":     entry["nature"],
        }

        # Scalar features
        for col in _SCALAR_COLS:
            row[col] = features.get(col, 0)

        # AST node-count columns
        for node, cnt in features.get("node_counts", {}).items():
            row[f"node_{node}"] = cnt

        records.append(row)

        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(labels_data)} files…")

    df = pd.DataFrame(records).fillna(0)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Features saved → {out_csv}  ({len(df)} rows, {len(df.columns)} cols)")
    return df


if __name__ == "__main__":
    process_dataset()
