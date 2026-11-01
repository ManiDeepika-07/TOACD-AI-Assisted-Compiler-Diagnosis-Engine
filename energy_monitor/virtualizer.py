"""
energy_monitor/virtualizer.py
==============================
Per-stage energy virtualizer for CD 2.0.

Given total measured/estimated energy and per-stage timing data, this module
attributes energy proportionally across the four pipeline stages:
  - compile          (Clang subprocess)
  - static_analysis  (regex + CFG)
  - ml_inference     (GradientBoosting predict)
  - report_gen       (JSON building + response)

Attribution method:
  stage_energy = total_energy × (stage_time / total_time)

This is virtual attribution — not direct hardware measurement per stage.
All outputs are clearly labeled as [VIRTUAL ATTRIBUTION].

Output format:
  {
    "total_joules":   float,
    "total_duration": float,
    "source":         "rapl" | "estimated",
    "stages": {
      "compile":         {"joules": float, "duration_s": float, "pct": float},
      "static_analysis": {"joules": float, "duration_s": float, "pct": float},
      "ml_inference":    {"joules": float, "duration_s": float, "pct": float},
      "report_gen":      {"joules": float, "duration_s": float, "pct": float},
    },
    "note": str
  }
"""

from config import ALL_STAGES


def virtualize(
    total_energy: dict,
    timings: dict[str, float],
) -> dict:
    """
    Attribute total energy across pipeline stages by timing proportion.

    Args:
        total_energy: Output dict from RaplMonitor.stop()
                      {"joules": ..., "source": ..., ...}
        timings:      Dict of {stage_name: duration_seconds}
                      e.g. {"compile": 0.45, "static_analysis": 0.02, ...}

    Returns:
        Virtualised breakdown dict.
    """
    total_joules   = total_energy.get("joules", 0.0)
    energy_source  = total_energy.get("source", "estimated")

    # Ensure all known stages are present (default 0 if stage wasn't timed)
    timed = {s: max(timings.get(s, 0.0), 0.0) for s in ALL_STAGES}
    total_time = sum(timed.values())

    stages_out = {}
    for stage in ALL_STAGES:
        dur = timed[stage]
        pct = (dur / total_time * 100) if total_time > 0 else 0.0
        joules = total_joules * (dur / total_time) if total_time > 0 else 0.0
        stages_out[stage] = {
            "joules":     round(joules, 6),
            "duration_s": round(dur, 4),
            "pct":        round(pct, 1),
        }

    return {
        "total_joules":   round(total_joules, 6),
        "total_duration": round(total_time, 4),
        "source":         energy_source,
        "stages":         stages_out,
        "note":           "[VIRTUAL ATTRIBUTION — proportional to stage timing]",
    }


def format_joules(j: float) -> str:
    """Human-readable joules string."""
    if j < 0.001:
        return f"{j * 1_000_000:.2f} µJ"
    if j < 1.0:
        return f"{j * 1000:.3f} mJ"
    return f"{j:.4f} J"


def format_grams(g: float) -> str:
    """Human-readable CO2 grams string."""
    if g < 0.001:
        return f"{g * 1000:.4f} µg CO₂"
    if g < 1.0:
        return f"{g * 1000:.3f} mg CO₂"
    return f"{g:.4f} g CO₂"
