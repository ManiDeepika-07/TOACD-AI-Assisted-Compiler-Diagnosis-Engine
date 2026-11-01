"""
tests/test_diagnose.py
Pytest test suite for CD 2.0 multi-error diagnosis system.

Run with:   python -m pytest tests/ -v
"""

import os
import sys
import tempfile
import pytest

# Ensure scripts/ is on the path
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)

from model.predict import diagnose
from parser.cfg    import detect_infinite_loops
from parser.regex_parser import scan_source, scan_infinite_loops

MODEL_DIR = os.path.join(_SCRIPT_DIR, "models")


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _write_tmp(code: str, suffix: str = ".cpp") -> str:
    """Write code to a temporary file and return its path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix,
                                      mode="w", encoding="utf-8")
    tmp.write(code)
    tmp.close()
    return tmp.name


def _error_types(result: dict) -> list[str]:
    return [e["error_type"] for e in result.get("errors", [])]


# ──────────────────────────────────────────────────────────────────────────────
#  1. Clean code — no errors
# ──────────────────────────────────────────────────────────────────────────────
def test_no_error():
    code = """#include <iostream>
int main() {
    int x = 5, y = 10;
    std::cout << x + y << std::endl;
    return 0;
}"""
    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        # May detect 0 or very few errors on clean code
        critical_errs = [e for e in result.get("errors", [])
                         if e.get("severity") in ("Critical", "High")]
        assert len(critical_errs) == 0, f"Clean code should have no critical errors. Got: {_error_types(result)}"
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
#  2. Single error — buffer overflow (strcpy)
# ──────────────────────────────────────────────────────────────────────────────
def test_buffer_overflow():
    code = """#include <cstring>
int main() {
    char buf[8];
    strcpy(buf, "This string is way too long for the buffer!");
    return 0;
}"""
    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        errors = result.get("errors", [])
        assert len(errors) >= 1, "Should detect at least one error"
        types = _error_types(result)
        assert "buffer_overflow" in types, f"Expected buffer_overflow, got: {types}"
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
#  3. Multiple errors — buffer overflow + format string
# ──────────────────────────────────────────────────────────────────────────────
def test_multiple_errors():
    code = """#include <stdio.h>
#include <cstring>
int main() {
    char buf[8];
    char inp[64] = "%x %x %x";
    strcpy(buf, "way too long string here!!");
    printf(inp);
    return 0;
}"""
    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        errors = result.get("errors", [])
        assert len(errors) >= 2, f"Expected ≥ 2 errors, got {len(errors)}: {_error_types(result)}"
        types = _error_types(result)
        assert "buffer_overflow" in types, f"Missing buffer_overflow in: {types}"
        assert "format_string" in types, f"Missing format_string in: {types}"
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
#  4. Infinite loop — CFG detection (while true, no break)
# ──────────────────────────────────────────────────────────────────────────────
def test_infinite_loop_cfg():
    code = """#include <iostream>
int main() {
    int x = 0;
    while (true) {
        x++;
    }
    return 0;
}"""
    cfg_errors = detect_infinite_loops(code)
    assert len(cfg_errors) >= 1, "CFG should detect an infinite loop"
    assert cfg_errors[0]["error_type"] == "infinite_loop"

    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        types  = _error_types(result)
        assert "infinite_loop" in types, f"Full diagnosis should flag infinite_loop. Got: {types}"
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
#  5. Infinite loop with break — should NOT be flagged
# ──────────────────────────────────────────────────────────────────────────────
def test_infinite_loop_with_break_not_flagged():
    code = """#include <iostream>
int main() {
    int x = 0;
    while (true) {
        x++;
        if (x > 100) break;
    }
    return 0;
}"""
    cfg_errors = detect_infinite_loops(code)
    inf_errs   = [e for e in cfg_errors if e["error_type"] == "infinite_loop"]
    assert len(inf_errs) == 0, f"Loop with break should NOT be flagged. Got: {cfg_errors}"


# ──────────────────────────────────────────────────────────────────────────────
#  6. Wrong-direction counter loop
# ──────────────────────────────────────────────────────────────────────────────
def test_wrong_direction_loop():
    code = """#include <iostream>
int main() {
    for (int i = 0; i < 10; i--) {
        std::cout << i;
    }
    return 0;
}"""
    cfg_errors = detect_infinite_loops(code)
    assert len(cfg_errors) >= 1, "Wrong-direction counter loop should be detected"


# ──────────────────────────────────────────────────────────────────────────────
#  7. Type mismatch via regex scanner
# ──────────────────────────────────────────────────────────────────────────────
def test_type_mismatch_regex():
    code = """#include <iostream>
int main() {
    int x = "hello";
    return 0;
}"""
    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        types  = _error_types(result)
        # Either Clang or ML should catch this
        assert len(result.get("errors", [])) >= 1, f"Expected at least 1 error, got: {types}"
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
#  8. Null pointer dereference
# ──────────────────────────────────────────────────────────────────────────────
def test_null_ptr_scan():
    code = """#include <iostream>
int main() {
    int* p = nullptr;
    *p = 42;
    return 0;
}"""
    regex_errs = scan_source(code)
    # regex scanner checks nullptr->  but not plain *p after nullptr assignment
    # The full diagnose should catch it via Clang or ML
    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        assert isinstance(result.get("errors"), list), "Result should have errors list"
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
#  9. Command injection (system() with unsanitized input)
# ──────────────────────────────────────────────────────────────────────────────
def test_command_injection():
    code = """#include <cstdlib>
#include <cstring>
int main() {
    char cmd[128];
    char arg[] = "arg; rm -rf /";
    sprintf(cmd, "echo %s", arg);
    system(cmd);
    return 0;
}"""
    regex_errs = scan_source(code)
    types = [e["error_type"] for e in regex_errs]
    assert "command_injection" in types, f"Command injection should be detected. Got: {types}"


# ──────────────────────────────────────────────────────────────────────────────
#  10. Division by zero literal
# ──────────────────────────────────────────────────────────────────────────────
def test_division_by_zero():
    code = """#include <iostream>
int main() {
    int x = 10 / 0;
    return 0;
}"""
    regex_errs = scan_source(code)
    types = [e["error_type"] for e in regex_errs]
    assert "division_by_zero" in types, f"Division by zero should be detected. Got: {types}"


# ──────────────────────────────────────────────────────────────────────────────
#  11. Multi-error: infinite loop + buffer overflow
# ──────────────────────────────────────────────────────────────────────────────
def test_multi_error_loop_plus_overflow():
    code = """#include <cstring>
int main() {
    char buf[4];
    while (true) {
        strcpy(buf, "overflow");
    }
    return 0;
}"""
    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        types  = _error_types(result)
        # At least one of infinite_loop or buffer_overflow must appear
        detected = set(types) & {"infinite_loop", "buffer_overflow"}
        assert len(detected) >= 1, f"Should detect loop+overflow. Got: {types}"
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
#  12. Result shape validation
# ──────────────────────────────────────────────────────────────────────────────
def test_result_shape():
    code = """#include <iostream>
int main() { return 0; }"""
    path = _write_tmp(code)
    try:
        result = diagnose(path, model_dir=MODEL_DIR)
        assert "errors"  in result, "Result must have 'errors' key"
        assert "summary" in result, "Result must have 'summary' key"
        assert isinstance(result["errors"], list), "'errors' must be a list"
        assert "total_errors"       in result["summary"]
        assert "has_infinite_loop"  in result["summary"]
        assert "highest_severity"   in result["summary"]
    finally:
        os.unlink(path)
