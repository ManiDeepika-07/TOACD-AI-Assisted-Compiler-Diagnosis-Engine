"""tests/test_ai_explainer_validator.py — Test AI Explainer, code fixes, and Clang validation."""
import pytest
from model.ai_explainer import generate_ai_explanation_and_fix
from model.fix_validator import validate_and_compare_fix

def test_ai_explainer_missing_semicolon():
    code = """#include <iostream>
int main() {
    int x = 10
    return 0;
}"""
    diag = {
        "errors": [{"line": 3, "error_type": "missing_semicolon", "message": "expected ';'"}]
    }
    ai_res = generate_ai_explanation_and_fix(code, diag)
    assert "explanation" in ai_res
    assert len(ai_res["likely_causes"]) > 0
    assert "suggested_code" in ai_res
    assert ";" in ai_res["suggested_code"]

def test_fix_validation_clang():
    orig_code = """#include <iostream>
int main() {
    int x = 10
    return 0;
}"""
    fixed_code = """#include <iostream>
int main() {
    int x = 10;
    return 0;
}"""
    orig_diag = {
        "errors": [{"line": 3, "error_type": "missing_semicolon", "message": "expected ';'"}]
    }
    val = validate_and_compare_fix(orig_code, fixed_code, orig_diag)
    assert val["status"] == "RESOLVED"
    assert val["security_verified"] is True
    assert val["remaining_error_count"] == 0
    assert "diff" in val
