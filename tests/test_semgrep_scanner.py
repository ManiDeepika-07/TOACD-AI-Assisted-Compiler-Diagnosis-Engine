"""tests/test_semgrep_scanner.py — Test Semgrep security analysis."""
import pytest
from security.semgrep_scanner import run_semgrep_security_scan

def test_clean_code_security():
    code = "#include <iostream>\nint main() { std::cout << 42; return 0; }"
    res = run_semgrep_security_scan(code)
    assert res["is_safe"] is True
    assert res["total_findings"] == 0

def test_buffer_overflow_detection():
    code = """#include <cstring>
int main() {
    char buf[4];
    strcpy(buf, "Too long for buffer");
    return 0;
}"""
    res = run_semgrep_security_scan(code)
    assert res["is_safe"] is False
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "semgrep.c.security.insecure-strcpy" in rule_ids
    assert any("CWE-120" in f["cwe"] for f in res["findings"])

def test_format_string_detection():
    code = """#include <cstdio>
int main() {
    char fmt[] = "%x %n";
    printf(fmt);
    return 0;
}"""
    res = run_semgrep_security_scan(code)
    assert res["is_safe"] is False
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "semgrep.c.security.format-string" in rule_ids

def test_command_injection_detection():
    code = """#include <cstdlib>
int main() {
    system("rm -rf /");
    return 0;
}"""
    res = run_semgrep_security_scan(code)
    assert res["is_safe"] is False
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "semgrep.c.security.command-injection" in rule_ids
