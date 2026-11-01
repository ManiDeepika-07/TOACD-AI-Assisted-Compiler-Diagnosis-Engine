"""
model/fix_validator.py
AI Fix Validation and Comparison engine for TOACD.

Implements Pipeline Stage 5 from Architecture:
  1. Security Check: Ensures AI fix does not introduce prompt injection or exploits.
  2. Clang Validation: Recompiles the AI-generated code with Clang.
  3. Comparison: Compares original compiler diagnostics vs new diagnostics.
  4. Unified Diff: Generates visual line-by-line diff.
"""

import os
import difflib
import tempfile
from typing import Dict, List, Any

from parser.clang_parser import run_clang, parse_clang_errors
from parser.cfg import detect_infinite_loops
from security.attack_detector import detect_prompt_injection
from security.semgrep_scanner import run_semgrep_security_scan


def validate_and_compare_fix(
    original_code: str,
    suggested_code: str,
    original_diagnostics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validates the AI-generated code fix:
      - Validates security of fix (Prompt Injection + Semgrep)
      - Recompiles via Clang
      - Evaluates error reduction and regression
      - Computes unified diff
    """
    if not suggested_code or suggested_code.strip() == "":
        return {
            "status": "FAILED",
            "status_badge": "badge-na",
            "status_message": "No suggested code was provided for validation.",
            "security_verified": False,
            "original_error_count": original_diagnostics.get("summary", {}).get("total_errors", 0),
            "remaining_error_count": original_diagnostics.get("summary", {}).get("total_errors", 0),
            "remaining_errors": original_diagnostics.get("errors", []),
            "diff": "",
            "suggested_code": original_code
        }

    # ── Step 1: Security Scan on Suggested Code ─────────────────────────────
    injection_check = detect_prompt_injection(suggested_code)
    semgrep_check = run_semgrep_security_scan(suggested_code)
    
    security_clean = (not injection_check["detected"]) and semgrep_check["is_safe"]

    # ── Step 2: Clang Re-compilation ────────────────────────────────────────
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".cpp", mode="w", encoding="utf-8")
    tmp.write(suggested_code)
    tmp.close()
    tmp_path = tmp.name

    new_errors = []
    try:
        ast_out, stderr_out = run_clang(tmp_path)
        clang_errs = parse_clang_errors(stderr_out, suggested_code)
        for ce in clang_errs:
            new_errors.append({
                "line": ce["line"],
                "col": ce["col"],
                "error_type": ce["error_type"],
                "message": f"Line {ce['line']}: {ce['message']}",
                "level": ce["level"]
            })
        
        # Also check infinite loops
        cfg_errs = detect_infinite_loops(suggested_code)
        for cf in cfg_errs:
            new_errors.append(cf)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    # ── Step 3: Comparison with Original Diagnostics ────────────────────────
    orig_errors = original_diagnostics.get("errors", [])
    orig_fatal = [e for e in orig_errors if e.get("level") == "error" or e.get("severity") in ["Critical", "High", "Medium", "Low"]]
    new_fatal = [e for e in new_errors if e.get("level") == "error"]
    new_warnings = [e for e in new_errors if e.get("level") == "warning"]

    orig_count = len(orig_errors)
    new_count = len(new_fatal)

    if new_count == 0 and security_clean:
        status = "RESOLVED"
        status_badge = "badge-resolved"
        if new_warnings:
            status_message = f"All compiler errors resolved! Clean compilation with {len(new_warnings)} compiler warning(s)."
        else:
            status_message = "All compiler errors resolved & verified secure. Clean Clang compilation!"
    elif new_count == 0 and not security_clean:
        status = "SYNTAX_RESOLVED_SECURITY_WARNING"
        status_badge = "badge-medium"
        status_message = "Syntax errors resolved cleanly, but security scan flagged potential issues."
    elif new_count < orig_count:
        status = "PARTIALLY_RESOLVED"
        status_badge = "badge-medium"
        status_message = f"Partially resolved: error count reduced from {orig_count} to {new_count}."
    elif new_count > orig_count:
        status = "REGRESSION"
        status_badge = "badge-critical"
        status_message = f"Regression: new compilation errors encountered ({new_count} vs original {orig_count})."
    else:
        status = "UNRESOLVED"
        status_badge = "badge-high"
    # ── Step 4: Unified Diff Calculation ────────────────────────────────────
    orig_lines = original_code.splitlines(keepends=True)
    fixed_lines = suggested_code.splitlines(keepends=True)
    diff_gen = difflib.unified_diff(
        orig_lines,
        fixed_lines,
        fromfile="Original Code",
        tofile="AI Suggested Fix",
        lineterm=""
    )
    diff_text = "\n".join(diff_gen)

    return {
        "status": status,
        "status_badge": status_badge,
        "status_message": status_message,
        "security_verified": security_clean,
        "security_details": {
            "injection_detected": injection_check["detected"],
            "semgrep_findings": semgrep_check.get("findings", [])
        },
        "original_error_count": orig_count,
        "remaining_error_count": new_count,
        "remaining_errors": new_fatal,
        "compiler_warnings": new_warnings,
        "diff": diff_text,
        "suggested_code": suggested_code
    }
