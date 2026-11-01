"""
config.py — Centralized configuration for CD 2.0.
All paths, model settings, compiler settings, and energy constants live here.
"""
import os

# ── Base paths ────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, "models")
MOCK_INC    = os.path.join(BASE_DIR, "mock_inc")
REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports_out")

# ── Compiler settings ─────────────────────────────────────────────────────────
CLANG_FLAGS       = ["-fsyntax-only", "-Wall", "-Wextra"]
CLANG_TIMEOUT_SEC = 30

# ── Energy monitoring settings ────────────────────────────────────────────────
# Estimated average TDP (Thermal Design Power) in Watts for a typical laptop CPU.
# Used when RAPL is unavailable (e.g. Windows). Adjust for your machine.
CPU_TDP_WATTS = 15.0

# Estimated fraction of TDP actually used during analysis (light workload).
CPU_UTILIZATION_FACTOR = 0.25

# Effective watts consumed during diagnosis
EFFECTIVE_WATTS = CPU_TDP_WATTS * CPU_UTILIZATION_FACTOR  # = 3.75 W

# Carbon intensity of electricity — global average (kgCO2 per kWh).
# Source: IEA World Average 2023 ≈ 0.475 kg CO2/kWh
# Change to your region's value for more accuracy.
GRID_CARBON_INTENSITY_KG_PER_KWH = 0.475

# ── Energy stage names ────────────────────────────────────────────────────────
STAGE_COMPILE  = "compile"
STAGE_STATIC   = "static_analysis"
STAGE_ML       = "ml_inference"
STAGE_REPORT   = "report_gen"
ALL_STAGES     = [STAGE_COMPILE, STAGE_STATIC, STAGE_ML, STAGE_REPORT]

# ── Flask settings ────────────────────────────────────────────────────────────
FLASK_HOST      = "0.0.0.0"
FLASK_PORT      = 5000
FLASK_DEBUG     = False
MAX_UPLOAD_MB   = 2

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"   # DEBUG / INFO / WARNING
