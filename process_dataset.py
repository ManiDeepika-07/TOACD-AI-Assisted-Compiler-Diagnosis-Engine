import os
import json
import pandas as pd
from ast_parser import get_ast_dump, extract_features


def process_dataset():
    dataset_dir = "data/dataset"
    labels_path = os.path.join(dataset_dir, "labels.json")

    if not os.path.exists(labels_path):
        print("Labels file not found! Run dataset_generator.py first.")
        return

    with open(labels_path, "r") as f:
        labels_data = json.load(f)

    records = []
    for idx, entry in enumerate(labels_data):
        file_path = os.path.join(dataset_dir, entry["file"])
        stdout, stderr = get_ast_dump(file_path)

        try:
            with open(file_path, "r", errors="ignore") as src:
                source_text = src.read()
        except Exception:
            source_text = ""

        # Pass stderr so Clang's own diagnostics become features
        features = extract_features(stdout, source_text, stderr)

        row = {
            "file":                    entry["file"],
            "error_type":              entry["error_type"],
            "severity":                entry["severity"],
            "category":                entry["category"],
            "nature":                  entry["nature"],
            # Structural
            "total_nodes":             features["total_nodes"],
            "depth_max":               features["depth_max"],
            "uninit_vars":             features["uninit_vars"],
            "null_ptrs":               features["null_ptrs"],
            # Loop / exit
            "has_while_true":          features["has_while_true"],
            "loop_without_exit":       features["loop_without_exit"],
            "loop_exit_count":         features["loop_exit_count"],
            # Type-cast
            "implicit_cast_count":     features["implicit_cast_count"],
            "cstyle_cast_count":       features["cstyle_cast_count"],
            "reinterpret_cast_count":  features["reinterpret_cast_count"],
            # Security function calls
            "strcpy_call":             features["strcpy_call"],
            "gets_call":               features["gets_call"],
            "sprintf_call":            features["sprintf_call"],
            "system_call":             features["system_call"],
            "malloc_call":             features["malloc_call"],
            "free_call":               features["free_call"],
            "printf_userctrl":         features["printf_userctrl"],
            # ── Clang stderr diagnostic flags (KEY NEW FEATURES) ──────────
            "stderr_has_error":        features["stderr_has_error"],
            "stderr_has_warning":      features["stderr_has_warning"],
            "stderr_error_count":      features["stderr_error_count"],
            "stderr_warning_count":    features["stderr_warning_count"],
            "stderr_missing_brace":    features["stderr_missing_brace"],
            "stderr_missing_semi":     features["stderr_missing_semi"],
            "stderr_expected_expr":    features["stderr_expected_expr"],
            "stderr_undeclared":       features["stderr_undeclared"],
            "stderr_type_mismatch":    features["stderr_type_mismatch"],
            "stderr_implicit_narrowing": features["stderr_implicit_narrowing"],
            "stderr_void_return":      features["stderr_void_return"],
            "stderr_return_type":      features["stderr_return_type"],
            "stderr_null_deref":       features["stderr_null_deref"],
            "stderr_uninit":           features["stderr_uninit"],
            "stderr_div_zero":         features["stderr_div_zero"],
            "stderr_deprecated":       features["stderr_deprecated"],
            "stderr_format_security":  features["stderr_format_security"],
            "stderr_buffer":           features["stderr_buffer"],
        }

        # Node-type columns
        for node, count in features["node_counts"].items():
            row[f"node_{node}"] = count

        records.append(row)

        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(labels_data)} files…")

    df = pd.DataFrame(records).fillna(0)
    df.to_csv("data/features.csv", index=False)
    print(f"Features extracted and saved to data/features.csv  ({len(df)} rows, {len(df.columns)} cols)")


if __name__ == "__main__":
    process_dataset()
