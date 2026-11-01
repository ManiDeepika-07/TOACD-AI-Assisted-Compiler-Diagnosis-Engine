import joblib
import pandas as pd
import sys
import os
import re
from ast_parser import get_ast_dump, extract_features

# ─────────────────────────────────────────────────────────────────────────────
#  FIX SUGGESTIONS — every error type is mapped
# ─────────────────────────────────────────────────────────────────────────────
FIX_SUGGESTIONS = {
    "no_error":
        "No obvious errors detected. Code looks clean!",
    "missing_semicolon":
        "Check for a missing ';' at the end of a statement. "
        "Most compilers point to the line *after* where it is needed.",
    "missing_brace":
        "A '{' or '}' is missing. Ensure every opening brace has a "
        "matching closing brace. Use a code formatter (e.g., clang-format) to locate issues quickly.",
    "undeclared_variable":
        "The variable is used before it is declared. Declare it with the "
        "correct type before first use (e.g., 'int myVar;').",
    "uninitialized_variable":
        "Initialize the variable before use (e.g., 'int x = 0;'). "
        "Uninitialized variables hold garbage values and can cause undefined behavior.",
    "assignment_in_condition":
        "Replace the assignment '=' inside a condition with a comparison '=='. "
        "To suppress the warning intentionally, wrap in extra parentheses: 'if ((x = val))'.",
    "out_of_bounds":
        "Ensure array/pointer accesses stay within allocated bounds. "
        "Validate indices before use. Consider using std::vector with .at() for automatic bounds checking.",
    "null_ptr_access":
        "Always check pointers before dereferencing: 'if (ptr != nullptr) { ... }'. "
        "Prefer smart pointers (std::unique_ptr / std::shared_ptr) to manage lifetime automatically.",
    "division_by_zero":
        "Guard division operations: 'if (divisor != 0) { result = a / divisor; }'. "
        "For floating-point code also handle NaN and Inf.",
    "infinite_loop":
        "The loop lacks a guaranteed exit. Add a 'break', 'return', or call 'exit()' "
        "when a termination condition is met. Verify that the loop variable is correctly "
        "modified each iteration (e.g., increment instead of decrement when counting up).",
    "type_mismatch":
        "Ensure variables and parameters use matching types. Avoid implicit narrowing "
        "conversions. Use explicit casts only when intentional: 'static_cast<int>(floatVal)'. "
        "Compile with '-Wall -Wextra' to catch hidden type warnings.",
    # ── Security errors ───────────────────────────────────────────────────────
    "buffer_overflow":
        "Replace unsafe functions (strcpy, gets, sprintf) with size-limited counterparts "
        "(strncpy, fgets, snprintf). Always validate that input length ≤ buffer size. "
        "Enable stack-canary protections (-fstack-protector-strong) and ASLR.",
    "use_after_free":
        "After calling free()/delete, set the pointer to nullptr immediately. "
        "Use smart pointers (std::unique_ptr) which automatically prevent use-after-free. "
        "Enable AddressSanitizer (-fsanitize=address) during testing.",
    "command_injection":
        "Never pass unsanitized user input to system(), popen(), or exec*(). "
        "Use parameterized APIs instead (e.g., execv with a fixed argv array). "
        "Whitelist acceptable input characters and reject everything else.",
    "format_string":
        "Never use user-supplied data as a printf format string. "
        "Always use a fixed format literal: 'printf(\"%s\", user_input)' instead of 'printf(user_input)'. "
        "Compile with '-Wformat-security' to catch these issues.",
    "integer_overflow":
        "Use checked arithmetic or types that cannot overflow (e.g., uint64_t for large counts). "
        "Always validate sizes before allocation: ensure (size + 1) does not wrap around. "
        "Enable UBSAN (-fsanitize=undefined) during development.",
    # ── Green / Sustainability ──────────────────────────────────────────────
    "energy_inefficiency":
        "[GREEN COMPILER WARNING] Deeply nested loops or complex structural patterns waste CPU cycles and energy. "
        "Consider refactoring your code (e.g., extracting functions, flattening loops, "
        "or optimizing the algorithm) to lower the O(N) complexity and reduce carbon footprint.",
}

# ─────────────────────────────────────────────────────────────────────────────
#  SECURITY RELEVANCE — every error type is mapped
# ─────────────────────────────────────────────────────────────────────────────
SECURITY_RELEVANCE = {
    "no_error":
        "None — No security concerns detected.",
    "missing_semicolon":
        "Low — Syntax error only; no direct security impact.",
    "missing_brace":
        "Low — Structural syntax error. May inadvertently expose code paths "
        "('goto fail' style bugs), but generally not exploitable.",
    "undeclared_variable":
        "Low — Causes a compile-time failure; cannot be exploited at runtime.",
    "uninitialized_variable":
        "Medium — Uninitialized memory may contain sensitive data from a prior "
        "stack/heap allocation, leading to information disclosure (CWE-457).",
    "assignment_in_condition":
        "Low-Medium — Can silently alter program logic, creating an unintended "
        "control-flow bypass that an attacker may trigger.",
    "out_of_bounds":
        "High — Out-of-bounds access can overwrite adjacent memory, enabling "
        "code execution (buffer overflow, CWE-119 / CWE-125 / CWE-787).",
    "null_ptr_access":
        "High — Dereferencing a null pointer crashes the process, enabling "
        "Denial-of-Service (DoS). On some platforms it is exploitable for "
        "privilege escalation (CWE-476).",
    "division_by_zero":
        "Medium — Causes process termination (DoS). In embedded / kernel code "
        "may trigger unhandled exceptions exploitable for privilege escalation.",
    "infinite_loop":
        "Medium — Consumes 100 % CPU, leading to Denial-of-Service (CWE-835). "
        "In server contexts this is a resource-exhaustion attack vector.",
    "type_mismatch":
        "Medium — Implicit type conversions can silently truncate data, "
        "changing program behavior in security-relevant ways (e.g., integer "
        "truncation bypassing length checks — CWE-197).",
    # ── Security errors ───────────────────────────────────────────────────────
    "buffer_overflow":
        "CRITICAL — Stack/heap buffer overflows can overwrite return addresses or "
        "vtable pointers, enabling arbitrary code execution (CWE-120 / CWE-787). "
        "Highest-severity vulnerability class.",
    "use_after_free":
        "CRITICAL — Use-after-free allows attackers to control freed memory and "
        "redirect execution (CWE-416). Frequently exploited in browser and kernel CVEs.",
    "command_injection":
        "CRITICAL — Unsanitized input passed to system() gives attackers full OS "
        "command execution with the process's privileges (CWE-78).",
    "format_string":
        "CRITICAL — Format-string bugs allow attackers to read arbitrary memory "
        "and write to arbitrary addresses via %n, leading to code execution (CWE-134).",
    "integer_overflow":
        "High — Integer overflows cause incorrect size calculations, leading to "
        "under-allocated buffers and subsequent heap corruption (CWE-190).",
    # ── Green / Sustainability ──────────────────────────────────────────────
    "energy_inefficiency":
        "N/A — This is a Green Compiler metric, not a direct security vulnerability. "
        "Green Compilers focus on sustainability by flagging energy-draining code.",
}


def diagnose(file_path, model_dir="models"):
    if not os.path.exists(file_path):
        print(f"[ERROR] File '{file_path}' not found.")
        return None

    # ── Load models ──────────────────────────────────────────────────────────
    model_type = joblib.load(os.path.join(model_dir, "error_classifier.pkl"))
    model_sev  = joblib.load(os.path.join(model_dir, "severity_classifier.pkl"))
    model_cat  = joblib.load(os.path.join(model_dir, "category_classifier.pkl"))
    model_nat  = joblib.load(os.path.join(model_dir, "nature_classifier.pkl"))
    feature_cols = joblib.load(os.path.join(model_dir, "feature_columns.pkl"))

    # ── Extract features ─────────────────────────────────────────────────────
    stdout, stderr = get_ast_dump(file_path)
    with open(file_path, "r", errors="ignore") as f:
        source_text = f.read()
    # Pass stderr so Clang's own diagnostics are included as features
    features = extract_features(stdout, source_text, stderr)

    row = {}
    for col in feature_cols:
        if col.startswith("node_"):
            node_name = col.replace("node_", "")
            row[col] = features["node_counts"].get(node_name, 0)
        elif col in features:
            row[col] = features[col]
        else:
            row[col] = 0

    X = pd.DataFrame([row])

   
    rule_based_pred = None

    # Source-level integer overflow: detect INT_MAX/INT_MIN used anywhere in source
    # (arithmetic like a+1 where a=INT_MAX also counts)
    _overflow_line = None
    _int_max_vars = set()
    for _lineno, _src_line in enumerate(source_text.splitlines(), start=1):
        _stripped = re.sub(r"//.*$", "", _src_line)
        # Direct arithmetic on limit macros
        if re.search(r"\b(INT_MAX|INT_MIN|LONG_MAX|LONG_MIN|UINT_MAX|SHRT_MAX)\s*[+\-\*]", _stripped) or \
           re.search(r"[+\-\*]\s*\b(INT_MAX|INT_MIN|LONG_MAX|LONG_MIN|UINT_MAX|SHRT_MAX)\b", _stripped):
            _overflow_line = _lineno
            break
        # Track vars assigned from INT_MAX
        _assign = re.search(r"\bint\s+(\w+)\s*=\s*(INT_MAX|INT_MIN)", _stripped)
        if _assign:
            _int_max_vars.add(_assign.group(1))
        # Arithmetic on a var that was assigned INT_MAX
        if _int_max_vars:
            for _v in _int_max_vars:
                if re.search(rf"\b{re.escape(_v)}\s*[+\-\*]", _stripped) or \
                   re.search(rf"[+\-\*]\s*\b{re.escape(_v)}\b", _stripped):
                    _overflow_line = _lineno
                    break
        if _overflow_line:
            break

    if _overflow_line:
        rule_based_pred = "integer_overflow"
    elif features.get("stderr_missing_brace"):
        rule_based_pred = "missing_brace"
    elif features.get("stderr_missing_semi"):
        rule_based_pred = "missing_semicolon"
    elif features.get("stderr_undeclared") and not _overflow_line:
        rule_based_pred = "undeclared_variable"
    elif features.get("stderr_type_mismatch") or features.get("stderr_implicit_narrowing"):
        rule_based_pred = "type_mismatch"
    elif features.get("stderr_uninit"):
        rule_based_pred = "uninitialized_variable"
    elif features.get("stderr_div_zero"):
        rule_based_pred = "division_by_zero"
    elif features.get("stderr_format_security"):
        rule_based_pred = "format_string"
    elif features.get("stderr_buffer"):
        rule_based_pred = "buffer_overflow"
    elif features.get("stderr_null_deref"):
        rule_based_pred = "null_ptr_access"
    elif features.get("energy_inefficient"):
        rule_based_pred = "energy_inefficiency"
    
    # Predict
    error_pred = model_type.predict(X)[0]
    
    # ── Safety Nets against ML Hallucinations ──
    syntax_errors = ["missing_brace", "missing_semicolon", "undeclared_variable", "type_mismatch"]
    logic_warnings = ["assignment_in_condition", "null_ptr_access", "uninitialized_variable", "division_by_zero"]
    
    if error_pred in syntax_errors and features.get("stderr_has_error") == 0:
        # ML predicted a syntax error, but Clang found no syntax errors!
        error_pred = "no_error"
    elif error_pred in logic_warnings and features.get("stderr_has_warning") == 0 and features.get("stderr_has_error") == 0:
        # ML predicted a logic/runtime error that Clang usually warns about, but Clang found nothing!
        error_pred = "no_error"
        
    if rule_based_pred:
        error_pred = rule_based_pred
        
   
    if error_pred == "infinite_loop" and features.get("loop_without_exit") == 0:
        error_pred = "no_error"

    # Predict auxiliary labels using the ML model
    sev_pred   = model_sev.predict(X)[0]
    cat_pred   = model_cat.predict(X)[0]
    nat_pred   = model_nat.predict(X)[0]

   
    OVERRIDE_LABELS = {
        "no_error":               ("Low", "N/A", "N/A"),
        "missing_brace":          ("Medium", "Compile-time", "Syntax"),
        "missing_semicolon":      ("Low", "Compile-time", "Syntax"),
        "undeclared_variable":    ("High", "Compile-time", "Syntax"),
        "uninitialized_variable": ("Medium", "Runtime", "Logical"),
        "type_mismatch":          ("Medium", "Compile-time", "Syntax"),
        "division_by_zero":       ("High", "Runtime", "Logical"),
        "format_string":          ("Critical", "Runtime", "Security"),
        "buffer_overflow":        ("Critical", "Runtime", "Security"),
        "null_ptr_access":        ("High", "Runtime", "Logical"),
        "integer_overflow":       ("High", "Runtime", "Security"),
        "energy_inefficiency":    ("Medium", "Green Compiler", "Sustainability"),
    }

    if error_pred in OVERRIDE_LABELS:
        s, c, n = OVERRIDE_LABELS[error_pred]
        sev_pred = s if sev_pred == "Low" or error_pred == "no_error" else sev_pred
        # Actually, let's just force the strict labels for perfect consistency
        sev_pred, cat_pred, nat_pred = s, c, n

    suggestion = FIX_SUGGESTIONS.get(
        error_pred,
        "Consult the compiler documentation and check for recent changes."
    )
    security   = SECURITY_RELEVANCE.get(
        error_pred,
        "Unknown — refer to OWASP / CWE for guidance."
    )

    result = {
        "file":            os.path.basename(file_path),
        "error_type":      error_pred,
        "severity":        sev_pred,
        "nature":          nat_pred,
        "category":        cat_pred,
        "security":        security,
        "suggestion":      suggestion,
    }

    print(f"\n{'=' * 55}")
    print(f"  AI Diagnosis — {result['file']}")
    print(f"{'=' * 55}")
    print(f"  Error Type  : {result['error_type']}")
    if error_pred == "integer_overflow" and _overflow_line:
        print(f"  Line        : {_overflow_line}")
    print(f"  Severity    : {result['severity']}")
    print(f"  Nature      : {result['nature']}")
    print(f"  Category    : {result['category']}")
    print(f"  Security    : {result['security']}")
    print(f"  Suggestion  : {result['suggestion']}")
    print(f"{'=' * 55}\n")

    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        diagnose(sys.argv[1])
    else:
        for sample in [
            "data/buggy_semicolon.cpp",
            "data/buggy_uninitialized.cpp",
            "data/correct_sample.cpp",
        ]:
            if os.path.exists(sample):
                diagnose(sample)
