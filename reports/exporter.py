"""
reports/exporter.py
====================
Export CD 2.0 diagnosis results to JSON, CSV, and plain-text formats.

All export functions accept the full result dict returned by model/predict.py
(augmented with energy data by app.py) and return a string ready for download.
"""

import json
import csv
import io
import datetime


# ── JSON export ───────────────────────────────────────────────────────────────

def to_json(result: dict, indent: int = 2) -> str:
    """Serialize full result dict to pretty-printed JSON."""
    exportable = _clean_for_export(result)
    return json.dumps(exportable, indent=indent, ensure_ascii=False, default=str)


# ── CSV export ────────────────────────────────────────────────────────────────

def to_csv(result: dict) -> str:
    """
    Export errors list as CSV.
    Columns: line, error_type, severity, category, nature, message, suggestion, security
    """
    buf = io.StringIO()
    fieldnames = [
        "line", "error_type", "severity", "category",
        "nature", "message", "suggestion", "security",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for err in result.get("errors", []):
        writer.writerow({k: err.get(k, "") for k in fieldnames})
    return buf.getvalue()


# ── Plain-text report ─────────────────────────────────────────────────────────

def to_text(result: dict) -> str:
    """Generate a structured plain-text diagnostic report."""
    lines = []
    ts    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("=" * 65)
    lines.append("  CD 2.0 — AI Compiler Diagnostic Report")
    lines.append(f"  Generated : {ts}")
    lines.append(f"  File      : {result.get('file', 'unknown')}")
    lines.append("=" * 65)

    # ── Summary ───────────────────────────────────────────────────────────────
    summary = result.get("summary", {})
    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total Errors    : {summary.get('total_errors', 0)}")
    lines.append(f"  Highest Severity: {summary.get('highest_severity', 'N/A')}")
    lines.append(f"  Infinite Loop   : {'YES' if summary.get('has_infinite_loop') else 'NO'}")

    # ── Errors ────────────────────────────────────────────────────────────────
    errors = result.get("errors", [])
    if errors:
        lines.append("")
        lines.append(f"DETECTED ISSUES  ({len(errors)} total)")
        lines.append("-" * 40)
        for i, err in enumerate(errors, 1):
            lines.append(f"\n  [{i}] Line {err.get('line','?')} — {err.get('error_type','?').upper()}")
            lines.append(f"       Severity : {err.get('severity','?')}  |  Category: {err.get('category','?')}  |  Nature: {err.get('nature','?')}")
            lines.append(f"       Message  : {err.get('message','')}")
            lines.append(f"       Suggestion: {err.get('suggestion','')}")
            lines.append(f"       Security : {err.get('security','')}")
    else:
        lines.append("")
        lines.append("  ✅  No errors detected. Code looks clean!")

    # ── Semgrep Security Findings ─────────────────────────────────────────────
    semgrep = result.get("semgrep_scan", {})
    if semgrep and semgrep.get("findings"):
        lines.append("")
        lines.append(f"SEMGREP SECURITY ANALYSIS  ({semgrep.get('total_findings', 0)} finding(s))")
        lines.append("-" * 40)
        lines.append(f"  Scanner Engine : {semgrep.get('engine', 'Semgrep')}")
        for i, f in enumerate(semgrep["findings"], 1):
            lines.append(f"\n  [SEC-{i}] Line {f.get('line','?')} — {f.get('rule_id','?')}")
            lines.append(f"         Severity : {f.get('severity','?')} | {f.get('cwe','')} | {f.get('owasp','')}")
            lines.append(f"         Finding  : {f.get('message','')}")
            if f.get('code_snippet'):
                lines.append(f"         Code     : {f.get('code_snippet')}")
            lines.append(f"         Remedy   : {f.get('recommendation','')}")

    # ── AI Explanation & Fix ──────────────────────────────────────────────────
    ai_diag = result.get("ai_diagnosis", {})
    if ai_diag and ai_diag.get("explanation"):
        lines.append("")
        lines.append("AI EXPLANATION & CORRECTION (Groq / Secure LLM)")
        lines.append("-" * 40)
        lines.append(f"  Engine          : {ai_diag.get('engine', 'AI Engine')}")
        lines.append(f"  Explanation     : {ai_diag.get('explanation')}")
        if ai_diag.get("likely_causes"):
            lines.append("  Likely Causes   :")
            for cause in ai_diag["likely_causes"]:
                lines.append(f"    • {cause}")
        if ai_diag.get("fix_explanation"):
            lines.append(f"  Fix Strategy    : {ai_diag.get('fix_explanation')}")

    # ── AI Fix Validation ────────────────────────────────────────────────────
    ai_val = result.get("ai_validation", {})
    if ai_val:
        lines.append("")
        lines.append("AI FIX VALIDATION (Clang Recompilation)")
        lines.append("-" * 40)
        lines.append(f"  Validation Status: {ai_val.get('status')} — {ai_val.get('status_message')}")
        lines.append(f"  Original Errors  : {ai_val.get('original_error_count', 0)}")
        lines.append(f"  Post-Fix Errors  : {ai_val.get('remaining_error_count', 0)}")
        lines.append(f"  Security Clean   : {'YES' if ai_val.get('security_verified') else 'NO'}")
        if ai_val.get("diff"):
            lines.append("\n  Unified Code Diff:")
            for dline in ai_val["diff"].splitlines()[:25]:
                lines.append(f"    {dline}")

    # ── Energy ────────────────────────────────────────────────────────────────
    energy = result.get("energy", {})
    if energy:
        lines.append("")
        lines.append("ENERGY & SUSTAINABILITY")
        lines.append("-" * 40)
        lines.append(f"  Total Energy    : {energy.get('joules', 0):.6f} J  {energy.get('note','')}")
        lines.append(f"  Average Power   : {energy.get('watts', 0):.4f} W")
        lines.append(f"  Duration        : {energy.get('duration_s', 0):.4f} s")

        carbon = result.get("carbon", {})
        if carbon:
            lines.append(f"  Carbon Estimate : {carbon.get('grams_co2', 0):.6f} g CO₂  {carbon.get('note','')}")
            lines.append(f"  Energy (kWh)    : {carbon.get('kwh', 0):.9f} kWh")

        virtual = result.get("energy_virtual", {})
        if virtual and virtual.get("stages"):
            lines.append("")
            lines.append("  Per-Stage Attribution  [VIRTUAL]:")
            for stage, data in virtual["stages"].items():
                lines.append(f"    {stage:<20} {data['joules']:.6f} J  ({data['pct']:.1f}%)  {data['duration_s']:.4f}s")

    lines.append("")
    lines.append("=" * 65)
    lines.append("  TOACD · AI-Assisted Compiler Diagnosis Engine")
    lines.append("=" * 65)
    return "\n".join(lines)


# ── Internal helper ───────────────────────────────────────────────────────────

def _clean_for_export(result: dict) -> dict:
    """Remove internal-only fields before export."""
    skip = {"severity_class"}
    cleaned = {}
    for k, v in result.items():
        if k == "errors":
            cleaned[k] = [
                {ek: ev for ek, ev in err.items() if ek not in skip}
                for err in v
            ]
        else:
            cleaned[k] = v
    return cleaned
