"""
app.py  —  CD 2.0 Flask application (fully upgraded)
Multi-error diagnosis API + premium web UI.
"""

from flask import Flask, request, render_template, jsonify
import os
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from model.predict import diagnose
from security.attack_detector import detect_prompt_injection
from energy_monitor.rapl import RaplMonitor
from energy_monitor.carbon import CarbonMonitor
from energy_monitor.virtualizer import virtualize
from reports.exporter import to_json, to_csv, to_text

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024   # 2 MB


# ──────────────────────────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/diagnose", methods=["POST"])
def run_diagnose():
    """
    Accepts:
      - multipart file upload  (field: 'file')
      - form field with code   (field: 'code')

    Returns JSON:
    {
        "file": str,
        "errors": [{line, error_type, message, severity, category, nature,
                    suggestion, security, severity_class}, ...],
        "summary": {total_errors, has_infinite_loop, highest_severity}
    }
    """
    if "file" in request.files and request.files["file"].filename:
        uploaded = request.files["file"]
        suffix   = os.path.splitext(uploaded.filename)[1] or ".cpp"
        tmp      = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        uploaded.save(tmp.name)
        tmp.close()
        file_path = tmp.name
        filename  = uploaded.filename

    elif request.form.get("code", "").strip():
        code = request.form["code"]
        tmp  = tempfile.NamedTemporaryFile(delete=False, suffix=".cpp",
                                           mode="w", encoding="utf-8")
        tmp.write(code)
        tmp.close()
        file_path = tmp.name
        filename  = "inline_code.cpp"

    else:
        return jsonify({"error": "No file or code provided."}), 400


    # Security check for prompt injection
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code_content = f.read()

    security_result = detect_prompt_injection(code_content)
   

    if security_result["detected"]:
        return jsonify({
            "error": "Security threat detected.",
            "security": security_result
        }), 403


    try:
        model_dir = os.path.join(SCRIPT_DIR, "models")
        
        # ── Energy tracking start ──
        rapl = RaplMonitor()
        carb = CarbonMonitor()
        rapl.start()
        carb.start()
        
        result    = diagnose(file_path, model_dir=model_dir)
        
        # ── Energy tracking end ──
        energy_data = rapl.stop()
        carbon_data = carb.stop(joules_measured=energy_data.get("joules", 0.0))
        
        # Merge energy results
        result["energy"] = energy_data
        result["carbon"] = carbon_data
        
        # Virtualize per-stage attribution based on timings
        if "timings" in result:
            result["energy_virtual"] = virtualize(energy_data, result["timings"])
            
    except Exception as exc:
        os.unlink(file_path)
        return jsonify({"error": str(exc)}), 500

    os.unlink(file_path)

    if "error" in result:
        return jsonify(result), 500

    result["filename"] = filename
    return jsonify(result)


# ── JSON-only API endpoint ─────────────────────────────────────────────────────
@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():
    """Programmatic JSON endpoint — same as /diagnose but JSON body supported."""
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "No 'code' field in JSON body."}), 400

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".cpp",
                                      mode="w", encoding="utf-8")
    tmp.write(code)
    tmp.close()
    file_path = tmp.name

    try:
        model_dir = os.path.join(SCRIPT_DIR, "models")
        
        rapl = RaplMonitor()
        carb = CarbonMonitor()
        rapl.start()
        carb.start()
        
        result    = diagnose(file_path, model_dir=model_dir)
        
        energy_data = rapl.stop()
        result["energy"] = energy_data
        result["carbon"] = carb.stop(joules_measured=energy_data.get("joules", 0.0))
        if "timings" in result:
            result["energy_virtual"] = virtualize(energy_data, result["timings"])
            
    except Exception as exc:
        os.unlink(file_path)
        return jsonify({"error": str(exc)}), 500

    os.unlink(file_path)
    result["filename"] = "api_input.cpp"
    return jsonify(result)


# ── Export endpoint ────────────────────────────────────────────────────────────

@app.route("/api/export", methods=["POST"])
def api_export():
    """Export diagnosis results to JSON, CSV, or Text."""
    data = request.get_json(silent=True) or {}
    fmt  = data.get("format", "json").lower()
    res  = data.get("result", {})

    if not res:
        return jsonify({"error": "No result data provided."}), 400

    if fmt == "csv":
        return to_csv(res), 200, {"Content-Type": "text/csv"}
    elif fmt == "text":
        return to_text(res), 200, {"Content-Type": "text/plain"}
    else:
        return to_json(res), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
