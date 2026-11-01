"""
model/predict.py
Multi-error prediction engine.

Pipeline for each input file:
  1. Run Clang → parse ALL stderr diagnostics (one per error line).
  2. Run regex scanner → catch additional heuristic issues.
  3. Run CFG analysis → detect infinite loops.
  4. Merge, deduplicate, rank by line number.
  5. If no errors found via rules → use ML model as fallback.
  6. Return structured JSON with errors list.
"""

import os
import sys
import time
import joblib
import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)

from parser.clang_parser  import run_clang, parse_clang_errors, extract_stderr_features, extract_ast_features
from parser.regex_parser  import scan_source, scan_infinite_loops, get_meta, FIX_SUGGESTIONS, SECURITY_RELEVANCE
from parser.cfg            import detect_infinite_loops

# ──────────────────────────────────────────────────────────────────────────────
#  Severity score for de-duplication priority
# ──────────────────────────────────────────────────────────────────────────────
_SEV_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "N/A": 0}

_SEVERITY_CLASS = {
    "Low":      "badge-low",
    "Medium":   "badge-medium",
    "High":     "badge-high",
    "Critical": "badge-critical",
    "N/A":      "badge-na",
}


# ──────────────────────────────────────────────────────────────────────────────
#  Model loading (singleton, lazy)
# ──────────────────────────────────────────────────────────────────────────────
_MODEL_CACHE: dict = {}


def _load_models(model_dir: str) -> dict:
    if model_dir in _MODEL_CACHE:
        return _MODEL_CACHE[model_dir]

    required = [
        "error_classifier.pkl",
        "feature_columns.pkl",
    ]
    for fname in required:
        if not os.path.exists(os.path.join(model_dir, fname)):
            _MODEL_CACHE[model_dir] = None
            return None

    models = {
        "type":     joblib.load(os.path.join(model_dir, "error_classifier.pkl")),
        "sev":      joblib.load(os.path.join(model_dir, "severity_classifier.pkl")),
        "cat":      joblib.load(os.path.join(model_dir, "category_classifier.pkl")),
        "nat":      joblib.load(os.path.join(model_dir, "nature_classifier.pkl")),
        "feat_cols":joblib.load(os.path.join(model_dir, "feature_columns.pkl")),
        "override": joblib.load(os.path.join(model_dir, "override_labels.pkl"))
                    if os.path.exists(os.path.join(model_dir, "override_labels.pkl"))
                    else {},
    }
    _MODEL_CACHE[model_dir] = models
    return models


# ──────────────────────────────────────────────────────────────────────────────
#  Feature vector builder for ML fallback
# ──────────────────────────────────────────────────────────────────────────────

def _build_feature_row(ast_feats: dict, stderr_feats: dict, feat_cols: list) -> pd.DataFrame:
    row = {}
    for col in feat_cols:
        if col.startswith("node_"):
            node_name = col.replace("node_", "")
            row[col] = ast_feats.get("node_counts", {}).get(node_name, 0)
        elif col in stderr_feats:
            row[col] = stderr_feats[col]
        elif col in ast_feats:
            row[col] = ast_feats[col]
        else:
            row[col] = 0
    return pd.DataFrame([row])


# ──────────────────────────────────────────────────────────────────────────────
#  ML fallback prediction (single label)
# ──────────────────────────────────────────────────────────────────────────────

def _ml_predict(ast_feats: dict, stderr_feats: dict, models: dict) -> dict | None:
    """Use the GBM model to predict the primary error type and metadata."""
    if not models:
        return None

    X = _build_feature_row(ast_feats, stderr_feats, models["feat_cols"])
    error_pred = models["type"].predict(X)[0]

    # Safety Nets against ML Hallucinations
    syntax_errors = ["missing_brace", "missing_semicolon", "undeclared_variable", "type_mismatch"]
    logic_warnings = ["assignment_in_condition", "null_ptr_access", "uninitialized_variable", "division_by_zero", "format_string"]
    
    if error_pred == "missing_brace" and stderr_feats.get("stderr_missing_brace", 0) == 0:
        error_pred = "no_error"
    elif error_pred == "missing_semicolon" and stderr_feats.get("stderr_missing_semi", 0) == 0:
        error_pred = "no_error"
    elif error_pred == "undeclared_variable" and stderr_feats.get("stderr_undeclared", 0) == 0:
        error_pred = "no_error"
    elif error_pred in logic_warnings and stderr_feats.get("stderr_has_warning") == 0 and stderr_feats.get("stderr_has_error") == 0:
        error_pred = "no_error"
    elif error_pred == "infinite_loop" and ast_feats.get("loop_without_exit", 0) == 0:
        error_pred = "no_error"

    if ast_feats.get("energy_inefficient"):
        error_pred = "energy_inefficiency"

    if error_pred == "no_error":
        return None  # ML says clean → no error entry

    meta = get_meta(error_pred)
    return {
        "line":       0,   # ML has no line info
        "col":        0,
        "error_type": error_pred,
        "message":    f"AI model detected: {error_pred.replace('_', ' ').title()}",
        "source":     "ml",
        **meta,
    }


# ──────────────────────────────────────────────────────────────────────────────
#  Error merge & dedup
# ──────────────────────────────────────────────────────────────────────────────

def _merge_errors(errors: list[dict]) -> list[dict]:
    """
    Deduplicate errors:
    - Same (line, error_type) → keep only the highest-severity one.
    - Sort by line number, then severity desc.
    """
    # First pass: map error_type to the best valid line number available
    type_lines = {}
    for e in errors:
        line = e.get("line", 0)
        etype = e.get("error_type", "unknown")
        if line > 0:
            if etype not in type_lines or type_lines[etype] > line:
                type_lines[etype] = line

    best: dict[tuple, dict] = {}
    for e in errors:
        etype = e.get("error_type", "unknown")
        # Assign best available line to ML predictions
        if e.get("line", 0) == 0 and etype in type_lines:
            e["line"] = type_lines[etype]
            e["message"] = e["message"].replace("Global:", f"Line {e['line']}:")
            
        key = (e.get("line", 0), etype)
        existing = best.get(key)
        if existing is None:
            best[key] = e
        else:
            if _SEV_RANK.get(e.get("severity","Low"), 1) > _SEV_RANK.get(existing.get("severity","Low"), 1):
                best[key] = e

    merged = sorted(best.values(), key=lambda x: (
        x.get("line", 9999) if x.get("line", 0) > 0 else 9999, 
        -_SEV_RANK.get(x.get("severity", "Low"), 1)
    ))
    return merged


# ──────────────────────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────────────────────

def diagnose(file_path: str, model_dir: str = "models") -> dict:
    """
    Full multi-error diagnosis of a C++ source file.

    Returns:
    {
        "file": "...",
        "errors": [
            {
                "line": int,
                "error_type": str,
                "message": str,
                "severity": str,   "category": str, "nature": str,
                "suggestion": str, "security": str,
                "severity_class": str,
            },
            ...
        ],
        "summary": {
            "total_errors": int,
            "has_infinite_loop": bool,
            "highest_severity": str,
        }
    }
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    # ── Read source ───────────────────────────────────────────────────────────
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            source_text = fh.read()
    except Exception as exc:
        return {"error": str(exc)}

    all_errors: list[dict] = []
    timings: dict[str, float] = {}

    # ── Layer 1: Clang stderr multi-error parse ───────────────────────────────
    _t0 = time.perf_counter()
    ast_text, stderr_text = run_clang(file_path)
    clang_errors = parse_clang_errors(stderr_text, source_text)
    for ce in clang_errors:
        etype = ce["error_type"]

        # Resolve 'unknown' clang errors using message keywords
        if etype == "unknown":
            msg_l = ce["message"].lower()
            if "';'" in msg_l or "semicolon" in msg_l:
                etype = "missing_semicolon"
            elif "'{'" in msg_l or "'}'" in msg_l:
                etype = "missing_brace"
            elif "undeclared" in msg_l or "not declared" in msg_l:
                etype = "undeclared_variable"
            elif "uninitialized" in msg_l:
                etype = "uninitialized_variable"
            elif "convert" in msg_l or "incompatible" in msg_l or "initialize" in msg_l:
                etype = "type_mismatch"
            elif "null" in msg_l and ("pointer" in msg_l or "deref" in msg_l):
                etype = "null_ptr_access"
            elif "division" in msg_l or "divide" in msg_l:
                etype = "division_by_zero"
            elif "format" in msg_l:
                etype = "format_string"
            elif "overflow" in msg_l or "buffer" in msg_l:
                etype = "buffer_overflow"
            elif "string" in msg_l or "literal" in msg_l or "token" in msg_l or "expected" in msg_l:
                # Unterminated string literal / unexpected token → syntax error
                etype = "missing_semicolon"
            else:
                # Still unknown — skip to avoid cluttering output
                continue

        meta = get_meta(etype)
        all_errors.append({
            "line":       ce["line"],
            "col":        ce["col"],
            "error_type": etype,
            "message":    f"Line {ce['line']}: {ce['message']}",
            "source":     "clang",
            **meta,
        })

    timings["compile"] = time.perf_counter() - _t0

    # ── Layer 2: Regex / heuristic scan ──────────────────────────────────────
    _t0 = time.perf_counter()
    regex_errors = scan_source(source_text)
    # Only add regex errors not already covered by Clang
    clang_lines  = {(e["line"], e["error_type"]) for e in all_errors}
    for re_err in regex_errors:
        if (re_err.get("line", 0), re_err.get("error_type")) not in clang_lines:
            re_err["source"] = "regex"
            all_errors.append(re_err)

    # ── Layer 3: CFG infinite-loop detection ──────────────────────────────────
    cfg_errors = detect_infinite_loops(source_text)
    cfg_lines  = {(e["line"], e["error_type"]) for e in all_errors}
    for ce in cfg_errors:
        if (ce.get("line", 0), ce.get("error_type")) not in cfg_lines:
            ce["source"] = "cfg"
            all_errors.append(ce)

    timings["static_analysis"] = time.perf_counter() - _t0

    # ── Layer 4: ML prediction ────────────────────────────────────────────────
    _t0 = time.perf_counter()
    models = _load_models(model_dir)
    if models:
        ast_feats    = extract_ast_features(ast_text, source_text)
        stderr_feats = extract_stderr_features(stderr_text)
        ml_result    = _ml_predict(ast_feats, stderr_feats, models)
        if ml_result:
            all_errors.append(ml_result)

    timings["ml_inference"] = time.perf_counter() - _t0

    # ── Merge & deduplicate ───────────────────────────────────────────────────
    _t0 = time.perf_counter()
    all_errors = _merge_errors(all_errors)

    # ── Enrich each error with severity_class ─────────────────────────────────
    for e in all_errors:
        sev = e.get("severity", "Low")
        e["severity_class"] = _SEVERITY_CLASS.get(sev, "badge-na")
        # Clean up internal fields
        e.pop("source", None)
        e.pop("col",    None)

    # ── Summary ───────────────────────────────────────────────────────────────
    has_inf  = any(e["error_type"] == "infinite_loop" for e in all_errors)
    severities = [e.get("severity", "Low") for e in all_errors]
    highest  = max(severities, key=lambda s: _SEV_RANK.get(s, 0)) if severities else "N/A"

    result = {
        "file":   os.path.basename(file_path),
        "errors": all_errors,
        "summary": {
            "total_errors":    len(all_errors),
            "has_infinite_loop": has_inf,
            "highest_severity":  highest,
        },
        "timings": timings,
    }

    # Backward-compat fields (for old code that reads top-level keys)
    if all_errors:
        primary = all_errors[0]
        result["error_type"] = primary["error_type"]
        result["severity"]   = primary["severity"]
        result["nature"]     = primary["nature"]
        result["category"]   = primary["category"]
        result["security"]   = primary["security"]
        result["suggestion"] = primary["suggestion"]
        result["severity_class"] = primary["severity_class"]
    else:
        meta = get_meta("no_error")
        result.update({
            "error_type": "no_error",
            "severity":   "Low",
            "nature":     "N/A",
            "category":   "N/A",
            "security":   meta["security"],
            "suggestion": meta["suggestion"],
            "severity_class": "badge-low",
        })

    timings["report_gen"] = time.perf_counter() - _t0

    # Console summary
    print(f"\n{'=' * 55}")
    print(f"  CD 2.0 Diagnosis — {result['file']}")
    print(f"{'=' * 55}")
    if all_errors:
        for i, e in enumerate(all_errors, 1):
            print(f"  [{i}] Line {e.get('line','?')} | {e['error_type']} | {e['severity']}")
            print(f"       {e['message'][:80]}")
    else:
        print("  [PASS] No errors detected.")
    print(f"{'=' * 55}\n")

    return result
