"""
energy_monitor/rapl.py
======================
RAPL (Running Average Power Limit) energy monitor.

On Linux with Intel CPUs, reads real hardware energy counters from:
  /sys/class/powercap/intel-rapl/*/energy_uj

On Windows / macOS / non-Intel or permission-denied systems, falls back to
a CPU-time proportional estimator using psutil + a configurable TDP value.

All results are returned as:
  {
    "joules":  float,        # Energy in Joules
    "watts":   float,        # Average power in Watts (joules / duration_s)
    "source":  "rapl" | "estimated",
    "note":    str           # Human-readable label for UI
  }
"""

import os
import sys
import time
import platform
import logging

log = logging.getLogger(__name__)

# ── Try importing psutil (soft dependency) ────────────────────────────────────
try:
    import psutil
    _PSUTIL_OK = True
except ImportError:
    _PSUTIL_OK = False
    log.warning("psutil not installed — CPU-time estimator will use wall-clock only.")


# ── RAPL paths (Linux only) ───────────────────────────────────────────────────
_RAPL_ROOT = "/sys/class/powercap/intel-rapl"


def _rapl_available() -> bool:
    """Return True if RAPL sysfs interface is readable on this system."""
    return platform.system() == "Linux" and os.path.isdir(_RAPL_ROOT)


def _read_rapl_uj(domain_path: str) -> int:
    """Read energy_uj counter from a RAPL domain directory."""
    energy_file = os.path.join(domain_path, "energy_uj")
    with open(energy_file, "r") as fh:
        return int(fh.read().strip())


def _rapl_domains() -> list[str]:
    """Return list of RAPL domain paths that have energy_uj files."""
    domains = []
    try:
        for entry in os.listdir(_RAPL_ROOT):
            path = os.path.join(_RAPL_ROOT, entry)
            if os.path.isfile(os.path.join(path, "energy_uj")):
                domains.append(path)
    except PermissionError:
        pass
    return domains


# ── CPU-time estimator (Windows / macOS fallback) ─────────────────────────────

def _estimate_joules_from_cputime(cpu_time_s: float, wall_time_s: float) -> tuple[float, float]:
    """
    Estimate energy consumed using:
      E = P × t
    where P = effective_watts from config, and t = wall_clock_time.

    Returns (joules, watts).
    """
    # Import here to avoid circular imports
    try:
        from config import EFFECTIVE_WATTS
    except ImportError:
        EFFECTIVE_WATTS = 3.75  # fallback default

    joules = EFFECTIVE_WATTS * wall_time_s
    watts  = EFFECTIVE_WATTS
    return joules, watts


# ── Public context-manager-style Monitor ─────────────────────────────────────

class RaplMonitor:
    """
    Context manager that measures energy for a code block.

    Usage:
        monitor = RaplMonitor()
        monitor.start()
        ... run code ...
        result = monitor.stop()
        # result = {"joules": ..., "watts": ..., "source": ..., "note": ...}
    """

    def __init__(self):
        self._start_uj: dict[str, int] = {}
        self._start_time: float = 0.0
        self._cpu_start: float = 0.0
        self._using_rapl: bool = False

    def start(self):
        """Begin measurement."""
        self._start_time = time.perf_counter()

        if _rapl_available():
            domains = _rapl_domains()
            if domains:
                self._using_rapl = True
                for d in domains:
                    try:
                        self._start_uj[d] = _read_rapl_uj(d)
                    except (PermissionError, FileNotFoundError):
                        self._using_rapl = False
                        break
                if self._using_rapl:
                    log.debug("RAPL monitoring active on %d domains.", len(domains))
                    return

        # Fallback: record CPU time via psutil or os.times()
        self._using_rapl = False
        if _PSUTIL_OK:
            proc = psutil.Process()
            ct = proc.cpu_times()
            self._cpu_start = ct.user + ct.system
        else:
            self._cpu_start = sum(os.times()[:2])  # user + system

    def stop(self) -> dict:
        """End measurement and return energy dict."""
        wall_time = time.perf_counter() - self._start_time

        if self._using_rapl:
            total_uj = 0
            for d, start_uj in self._start_uj.items():
                try:
                    end_uj   = _read_rapl_uj(d)
                    delta_uj = end_uj - start_uj
                    # Handle counter wrap-around (max_energy_range_uj)
                    if delta_uj < 0:
                        try:
                            max_path = os.path.join(d, "max_energy_range_uj")
                            with open(max_path) as fh:
                                max_uj = int(fh.read().strip())
                            delta_uj += max_uj
                        except Exception:
                            delta_uj = abs(delta_uj)
                    total_uj += delta_uj
                except Exception:
                    pass

            joules = total_uj / 1_000_000.0  # µJ → J
            watts  = joules / wall_time if wall_time > 0 else 0.0
            return {
                "joules":       round(joules, 6),
                "watts":        round(watts, 4),
                "duration_s":   round(wall_time, 4),
                "source":       "rapl",
                "note":         "[MEASURED via Intel RAPL]",
            }

        # Estimator path
        if _PSUTIL_OK:
            proc = psutil.Process()
            ct   = proc.cpu_times()
            cpu_time = (ct.user + ct.system) - self._cpu_start
        else:
            cpu_time = sum(os.times()[:2]) - self._cpu_start

        joules, watts = _estimate_joules_from_cputime(cpu_time, wall_time)
        return {
            "joules":       round(joules, 6),
            "watts":        round(watts, 4),
            "duration_s":   round(wall_time, 4),
            "source":       "estimated",
            "note":         "[ESTIMATED — CPU-time × TDP model]",
        }


# ── Convenience function ──────────────────────────────────────────────────────

def measure_block(fn, *args, **kwargs) -> tuple:
    """
    Run fn(*args, **kwargs), return (result, energy_dict).
    """
    monitor = RaplMonitor()
    monitor.start()
    result = fn(*args, **kwargs)
    energy = monitor.stop()
    return result, energy
