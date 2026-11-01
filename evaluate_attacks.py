"""
evaluate_attacks.py
Standalone CLI runner for TOACD Security Layer Attack Metrics & Benchmark.

Usage:
    python evaluate_attacks.py
"""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from security.attack_evaluator import evaluate_attacks, save_evaluation_reports


def main():
    print("=" * 65)
    print("  TOACD Security Layer — Attack Metrics & Evaluation Suite")
    print("=" * 65)

    results = evaluate_attacks()
    m = results["metrics"]
    cm = results["confusion_matrix"]
    cb = results["category_breakdown"]

    print(f"\n[+] Evaluated {results['total_evaluated']} samples in {results['evaluation_duration_ms']} ms\n")

    print("--- CONFUSION MATRIX ---")
    print(f"  True Positives  (TP) : {cm['true_positives']:>3}  (Attacks correctly blocked)")
    print(f"  True Negatives  (TN) : {cm['true_negatives']:>3}  (Safe code correctly allowed)")
    print(f"  False Positives (FP) : {cm['false_positives']:>3}  (Safe code incorrectly blocked)")
    print(f"  False Negatives (FN) : {cm['false_negatives']:>3}  (Attacks missed)")

    print("\n--- PERFORMANCE METRICS ---")
    print(f"  Accuracy    : {m['accuracy_pct']:>6.2f}%  ({cm['true_positives'] + cm['true_negatives']}/{results['total_evaluated']})")
    print(f"  Precision   : {m['precision']:>6.4f}")
    print(f"  Recall (Sens): {m['recall']:>5.4f}")
    print(f"  Specificity : {m['specificity']:>6.4f}")
    print(f"  F1-Score    : {m['f1_score']:>6.4f}")
    print(f"  FPR / FNR   : {m['false_positive_rate']:.4f} / {m['false_negative_rate']:.4f}")

    print("\n--- CATEGORY BREAKDOWN ---")
    print(f"  {'Category':<26} | {'Samples':<8} | {'Correct':<8} | {'Accuracy':<8}")
    print("  " + "-" * 56)
    for cat, s in cb.items():
        print(f"  {cat:<26} | {s['total_samples']:<8} | {s['correct']:<8} | {s['accuracy_pct']}%")

    json_path, md_path = save_evaluation_reports(results, output_dir=os.path.join(SCRIPT_DIR, "reports"))
    print("\n[+] Evaluation reports successfully saved:")
    print(f"    - JSON: {json_path}")
    print(f"    - Markdown: {md_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
