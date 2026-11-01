"""
energy_monitor/carbon.py
========================
Carbon emissions estimator for CD 2.0 diagnosis sessions.

Priority order:
  1. CodeCarbon library (if installed) — most accurate, uses region data
  2. Formula fallback: E_kWh × grid_carbon_intensity_kg_per_kWh

Results format:
  {
    "kg_co2":   float,   # kilograms of CO2 equivalent
    "kwh":      float,   # kilowatt-hours consumed
    "grams_co2": float,  # grams of CO2 (for display)
    "source":   "codecarbon" | "estimated",
    "note":     str
  }
"""

import logging

log = logging.getLogger(__name__)

# Try importing codecarbon (optional dependency)
try:
    from codecarbon import EmissionsTracker as _CCTracker
    _CODECARBON_OK = True
except ImportError:
    _CODECARBON_OK = False
    log.info("codecarbon not installed — using formula-based carbon estimation.")

try:
    from config import GRID_CARBON_INTENSITY_KG_PER_KWH
except ImportError:
    GRID_CARBON_INTENSITY_KG_PER_KWH = 0.475  # IEA world average


# ── CodeCarbon-backed tracker ─────────────────────────────────────────────────

class _CodeCarbonTracker:
    """Thin wrapper around codecarbon.EmissionsTracker."""

    def __init__(self):
        self._tracker = _CCTracker(
            project_name="cd2_diagnosis",
            measure_power_secs=1,
            log_level="error",
            save_to_file=False,
            tracking_mode="process",
        )
        self._running = False

    def start(self):
        try:
            self._tracker.start()
            self._running = True
        except Exception as exc:
            log.warning("CodeCarbon start failed: %s", exc)
            self._running = False

    def stop(self) -> dict:
        if not self._running:
            return _empty_result("codecarbon")
        try:
            emissions = self._tracker.stop()   # kg CO2
            kwh = getattr(self._tracker, "_total_energy", None)
            if kwh is None:
                # Derive from emissions and intensity
                kwh = emissions / GRID_CARBON_INTENSITY_KG_PER_KWH if GRID_CARBON_INTENSITY_KG_PER_KWH else 0.0
            return {
                "kg_co2":    round(float(emissions), 9),
                "kwh":       round(float(kwh), 9),
                "grams_co2": round(float(emissions) * 1000, 6),
                "source":    "codecarbon",
                "note":      "[MEASURED via CodeCarbon]",
            }
        except Exception as exc:
            log.warning("CodeCarbon stop failed: %s", exc)
            return _empty_result("codecarbon")


# ── Formula-based fallback ────────────────────────────────────────────────────

class _FormulaTracker:
    """Simple formula: E_kWh = (watts × seconds) / 3600 / 1000  → CO2 = E × intensity."""

    def __init__(self):
        self._energy_joules: float = 0.0

    def update(self, joules: float):
        """Feed in measured/estimated joules from the RAPL monitor."""
        self._energy_joules = joules

    def compute(self) -> dict:
        kwh    = self._energy_joules / 3_600_000.0   # J → kWh
        kg_co2 = kwh * GRID_CARBON_INTENSITY_KG_PER_KWH
        return {
            "kg_co2":    round(kg_co2, 9),
            "kwh":       round(kwh, 9),
            "grams_co2": round(kg_co2 * 1000, 6),
            "source":    "estimated",
            "note":      "[ESTIMATED — kWh × grid intensity formula]",
        }


# ── Unified CarbonMonitor ─────────────────────────────────────────────────────

class CarbonMonitor:
    """
    Unified carbon monitor. Uses CodeCarbon if available, formula otherwise.

    Usage:
        cm = CarbonMonitor()
        cm.start()
        ... run code ...
        result = cm.stop(joules_measured=energy["joules"])
    """

    def __init__(self):
        self._formula  = _FormulaTracker()
        self._cc_ok    = False
        if _CODECARBON_OK:
            try:
                self._cc = _CodeCarbonTracker()
                self._cc_ok = True
            except Exception:
                self._cc_ok = False

    def start(self):
        if self._cc_ok:
            self._cc.start()

    def stop(self, joules_measured: float = 0.0) -> dict:
        if self._cc_ok:
            result = self._cc.stop()
            if result["kg_co2"] > 0:
                return result
        # Formula fallback
        self._formula.update(joules_measured)
        return self._formula.compute()


# ── Helper ────────────────────────────────────────────────────────────────────

def _empty_result(source: str) -> dict:
    return {"kg_co2": 0.0, "kwh": 0.0, "grams_co2": 0.0, "source": source, "note": "No data"}
