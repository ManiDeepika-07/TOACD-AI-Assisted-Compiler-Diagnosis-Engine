"""
app.py — TOACD (AI-Assisted Compiler Diagnosis Engine) Flask Application
Features:
  1. Multi-error Compiler Diagnosis (Clang + Regex + CFG + ML)
  2. Security Layer: Prompt Injection & Policy Bypass detection and attack blocking/logging
  3. Semgrep Security Scanning: Comprehensive C/C++ security vulnerability checks (CWEs/OWASP)
  4. Groq API + Secure LLM: AI Explanation, root causes, and C++ code correction
  5. AI Fix Validation: Recompilation using Clang, security re-check, and diff comparison
  6. Attack Metrics & Evaluation: Precision, Recall, Accuracy, F1-Score, Confusion Matrix
  7. RAPL Energy & CodeCarbon Footprint tracking
"""

import os
import sys
import tempfile
from flask import Flask, request, render_template, jsonify

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from model.predict import diagnose
from security.attack_detector import detect_prompt_injection, log_attack, get_attack_logs, get_attack_statistics
from security.semgrep_scanner import run_semgrep_security_scan
from model.ai_explainer import generate_ai_explanation_and_fix
from model.fix_validator import validate_and_compare_fix
from security.attack_evaluator import evaluate_attacks
from energy_monitor.rapl import RaplMonitor
from energy_monitor.carbon import CarbonMonitor
from energy_monitor.virtualizer import virtualize
from reports.exporter import to_json, to_csv, to_text

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024   # 2 MB Limit


# ──────────────────────────────────────────────────────────────────────────────
#  Core Diagnosis Pipeline Helper
# ──────────────────────────────────────────────────────────────────────────────

def process_code_diagnosis(file_path: str, filename: str, code_content: str, groq_key: str = None, groq_model: str = None):
    """
    Executes the complete 6-stage TOACD pipeline:
      1. Security Layer (Prompt Injection / Bypass Blocking)
      2. Compiler Diagnosis Engine (Clang + Regex + CFG + ML)
      3. Energy & Carbon Footprint Monitoring
      4. Enhanced Security Analysis (Semgrep Scan)
      5. Groq API + LLM AI Explanation & Correction
      6. AI Fix Validation & Comparison
    """
    # ── Stage 1: Security Layer ──
    security_result = detect_prompt_injection(code_content)
    if security_result["detected"]:
        attack_id = log_attack(security_result, snippet=code_content)
        security_result["attack_id"] = attack_id
        return {
            "error": "Security threat detected: Prompt injection / policy bypass blocked.",
            "security": security_result
        }, 403

    model_dir = os.path.join(SCRIPT_DIR, "models")

    # ── Energy tracking start ──
    rapl = RaplMonitor()
    carb = CarbonMonitor()
    rapl.start()
    carb.start()

    # ── Stage 2: Compiler Diagnosis Engine ──
    result = diagnose(file_path, model_dir=model_dir)

    # ── Energy tracking end ──
    energy_data = rapl.stop()
    carbon_data = carb.stop(joules_measured=energy_data.get("joules", 0.0))
    result["energy"] = energy_data
    result["carbon"] = carbon_data
    if "timings" in result:
        result["energy_virtual"] = virtualize(energy_data, result["timings"])

    # ── Stage 3: Semgrep Security Scanning ──
    semgrep_result = run_semgrep_security_scan(code_content)
    result["semgrep_scan"] = semgrep_result

    # ── Stage 4: Groq API + LLM AI Explanation & Code Fix ──
    ai_result = generate_ai_explanation_and_fix(
        source_code=code_content,
        diagnostics=result,
        semgrep_findings=semgrep_result.get("findings", []),
        api_key=groq_key,
        model=groq_model
    )
    result["ai_diagnosis"] = ai_result

    # ── Stage 5: AI Fix Validation + Comparison (Recompilation) ──
    if ai_result and "suggested_code" in ai_result:
        validation_result = validate_and_compare_fix(
            original_code=code_content,
            suggested_code=ai_result["suggested_code"],
            original_diagnostics=result
        )
        result["ai_validation"] = validation_result

    result["filename"] = filename
    result["original_code"] = code_content
    return result, 200


# ──────────────────────────────────────────────────────────────────────────────
#  Flask Web Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/diagnose", methods=["POST"])
def run_diagnose():
    """Form / Multipart file upload endpoint."""
    groq_key = request.headers.get("X-Groq-Api-Key") or request.form.get("groq_key")
    groq_model = request.form.get("groq_model")

    if "file" in request.files and request.files["file"].filename:
        uploaded = request.files["file"]
        suffix = os.path.splitext(uploaded.filename)[1] or ".cpp"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        uploaded.save(tmp.name)
        tmp.close()
        file_path = tmp.name
        filename = uploaded.filename

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code_content = f.read()

    elif request.form.get("code", "").strip():
        code_content = request.form["code"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".cpp", mode="w", encoding="utf-8")
        tmp.write(code_content)
        tmp.close()
        file_path = tmp.name
        filename = "inline_code.cpp"

    else:
        return jsonify({"error": "No file or code provided."}), 400

    try:
        data, status_code = process_code_diagnosis(
            file_path=file_path,
            filename=filename,
            code_content=code_content,
            groq_key=groq_key,
            groq_model=groq_model
        )
        return jsonify(data), status_code
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    finally:
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception:
                pass


# ── JSON-only API Endpoint ────────────────────────────────────────────────────
@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():
    """Programmatic JSON endpoint."""
    data = request.get_json(silent=True) or {}
    code_content = data.get("code", "")
    if not code_content.strip():
        return jsonify({"error": "No 'code' field provided in JSON body."}), 400

    groq_key = request.headers.get("X-Groq-Api-Key") or data.get("groq_key")
    groq_model = data.get("groq_model")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".cpp", mode="w", encoding="utf-8")
    tmp.write(code_content)
    tmp.close()
    file_path = tmp.name

    try:
        res_data, status_code = process_code_diagnosis(
            file_path=file_path,
            filename="api_input.cpp",
            code_content=code_content,
            groq_key=groq_key,
            groq_model=groq_model
        )
        return jsonify(res_data), status_code
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    finally:
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception:
                pass


# ── Security & Semgrep API Endpoints ──────────────────────────────────────────
@app.route("/api/semgrep_scan", methods=["POST"])
def api_semgrep_scan():
    """Standalone Semgrep security scan endpoint."""
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code.strip():
        return jsonify({"error": "No code provided."}), 400

    report = run_semgrep_security_scan(code)
    return jsonify(report)


# ── Attack Metrics & Benchmark Evaluation Endpoints ───────────────────────────
@app.route("/api/attack_metrics", methods=["GET"])
def api_attack_metrics():
    """Returns historical logged attack statistics and standard benchmark metrics."""
    stats = get_attack_statistics()
    eval_benchmark = evaluate_attacks()
    return jsonify({
        "status": "success",
        "historical_stats": stats,
        "benchmark_evaluation": eval_benchmark
    })


@app.route("/api/evaluate_attacks", methods=["POST"])
def api_run_evaluation():
    """Triggers an on-demand re-evaluation of the security benchmark suite."""
    eval_benchmark = evaluate_attacks()
    return jsonify(eval_benchmark)


# ── AI Code Fix & Validation Endpoint ─────────────────────────────────────────
@app.route("/api/ai_fix", methods=["POST"])
def api_ai_fix():
    """Generates AI fix and runs validation comparison on given code."""
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    errors = data.get("errors", [])
    groq_key = request.headers.get("X-Groq-Api-Key") or data.get("groq_key")
    groq_model = data.get("groq_model")

    if not code.strip():
        return jsonify({"error": "No code provided."}), 400

    # 1. Semgrep scan
    semgrep_res = run_semgrep_security_scan(code)

    # 2. AI Fix
    ai_fix = generate_ai_explanation_and_fix(
        source_code=code,
        diagnostics={"errors": errors},
        semgrep_findings=semgrep_res.get("findings", []),
        api_key=groq_key,
        model=groq_model
    )

    # 3. Validation
    validation = validate_and_compare_fix(
        original_code=code,
        suggested_code=ai_fix.get("suggested_code", code),
        original_diagnostics={"errors": errors, "summary": {"total_errors": len(errors)}}
    )

    return jsonify({
        "semgrep_scan": semgrep_res,
        "ai_diagnosis": ai_fix,
        "ai_validation": validation
    })


# ── Report Export Endpoint ────────────────────────────────────────────────────
@app.route("/api/export", methods=["POST"])
def api_export():
    """Export complete diagnosis results to JSON, CSV, or Text format."""
    data = request.get_json(silent=True) or {}
    fmt = data.get("format", "json").lower()
    res = data.get("result", {})

    if not res:
        return jsonify({"error": "No result data provided."}), 400

    if fmt == "csv":
        return to_csv(res), 200, {"Content-Type": "text/csv", "Content-Disposition": "attachment; filename=toacd_report.csv"}
    elif fmt == "text":
        return to_text(res), 200, {"Content-Type": "text/plain", "Content-Disposition": "attachment; filename=toacd_report.txt"}
    else:
        return to_json(res), 200, {"Content-Type": "application/json", "Content-Disposition": "attachment; filename=toacd_report.json"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
