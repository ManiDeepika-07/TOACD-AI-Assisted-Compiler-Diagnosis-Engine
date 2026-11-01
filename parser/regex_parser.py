"""
parser/regex_parser.py
Fast regex-based source code scan that runs even when Clang is unavailable.
Produces a list of suspected errors with line numbers.
"""
import re


# ──────────────────────────────────────────────────────────────────────────────
#  Error type metadata
# ──────────────────────────────────────────────────────────────────────────────
_META = {
    "missing_semicolon":       ("Low",      "Compile-time", "Syntax"),
    "missing_brace":           ("Medium",   "Compile-time", "Syntax"),
    "undeclared_variable":     ("High",     "Compile-time", "Syntax"),
    "uninitialized_variable":  ("Medium",   "Runtime",      "Logical"),
    "type_mismatch":           ("Medium",   "Compile-time", "Syntax"),
    "division_by_zero":        ("High",     "Runtime",      "Logical"),
    "null_ptr_access":         ("High",     "Runtime",      "Logical"),
    "infinite_loop":           ("High",     "Runtime",      "Logical"),
    "assignment_in_condition": ("Medium",   "Runtime",      "Logical"),
    "out_of_bounds":           ("High",     "Runtime",      "Logical"),
    "buffer_overflow":         ("Critical", "Runtime",      "Security"),
    "use_after_free":          ("Critical", "Runtime",      "Security"),
    "command_injection":       ("Critical", "Runtime",      "Security"),
    "format_string":           ("Critical", "Runtime",      "Security"),
    "integer_overflow":        ("High",     "Runtime",      "Security"),
    "invalid_directive":       ("High",     "Compile-time", "Syntax"),
    "missing_main":            ("High",     "Compile-time", "Syntax"),
    "energy_inefficiency":     ("Medium",   "Green Compiler", "Sustainability"),
    "no_error":                ("Low",      "N/A",          "N/A"),
}

FIX_SUGGESTIONS = {
    "no_error":
        "No obvious errors detected. Code looks clean!",
    "missing_semicolon":
        "Check for a missing ';' at the end of a statement. "
        "Most compilers point to the line *after* where it is needed.",
    "missing_brace":
        "A '{' or '}' is missing. Ensure every opening brace has a matching closing brace. "
        "Use clang-format to locate issues quickly.",
    "undeclared_variable":
        "The variable is used before it is declared. Declare it with the correct type "
        "before first use (e.g., 'int myVar;').",
    "uninitialized_variable":
        "Initialize the variable before use (e.g., 'int x = 0;'). "
        "Uninitialized variables hold garbage values and can cause undefined behavior.",
    "assignment_in_condition":
        "Replace the assignment '=' inside a condition with a comparison '=='. "
        "To suppress the warning intentionally, wrap in extra parentheses: 'if ((x = val))'.",
    "out_of_bounds":
        "Ensure array/pointer accesses stay within allocated bounds. "
        "Validate indices before use. Consider std::vector with .at() for automatic bounds checking.",
    "null_ptr_access":
        "Always check pointers before dereferencing: 'if (ptr != nullptr) { ... }'. "
        "Prefer smart pointers (std::unique_ptr / std::shared_ptr) to manage lifetime automatically.",
    "division_by_zero":
        "Guard division operations: 'if (divisor != 0) { result = a / divisor; }'. "
        "For floating-point code also handle NaN and Inf.",
    "infinite_loop":
        "The loop lacks a guaranteed exit. Add a 'break', 'return', or call 'exit()' "
        "when a termination condition is met. Verify the loop variable is correctly modified "
        "each iteration.",
    "type_mismatch":
        "Ensure variables and parameters use matching types. Avoid implicit narrowing conversions. "
        "Use explicit casts only when intentional: 'static_cast<int>(floatVal)'. "
        "Compile with '-Wall -Wextra' to catch hidden type warnings.",
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
        "Always validate sizes before allocation. Enable UBSAN (-fsanitize=undefined) during development.",
    "invalid_directive":
        "Check for typos in preprocessor directives (e.g., #includ instead of #include).",
    "missing_main":
        "Every C++ program must have an 'int main()' function as its entry point. Ensure 'main' is defined.",
    "energy_inefficiency":
        "[GREEN COMPILER WARNING] Deeply nested loops or complex structural patterns waste CPU cycles and energy. "
        "Consider refactoring your code (e.g., extracting functions, flattening loops, "
        "or optimizing the algorithm) to lower the O(N) complexity and reduce carbon footprint.",
}

SECURITY_RELEVANCE = {
    "no_error":               "None — No security concerns detected.",
    "missing_semicolon":      "Low — Syntax error only; no direct security impact.",
    "missing_brace":          "Low — Structural syntax error. May inadvertently expose code paths, but generally not exploitable.",
    "undeclared_variable":    "Low — Causes a compile-time failure; cannot be exploited at runtime.",
    "uninitialized_variable": "Medium — Uninitialized memory may contain sensitive data from a prior stack/heap allocation (CWE-457).",
    "assignment_in_condition":"Low-Medium — Can silently alter program logic, creating an unintended control-flow bypass.",
    "out_of_bounds":          "High — Out-of-bounds access can overwrite adjacent memory, enabling code execution (CWE-119/CWE-787).",
    "null_ptr_access":        "High — Dereferencing a null pointer crashes the process (DoS). On some platforms exploitable for privilege escalation (CWE-476).",
    "division_by_zero":       "Medium — Causes process termination (DoS). In embedded/kernel code may trigger unhandled exceptions (CWE-369).",
    "infinite_loop":          "Medium — Consumes 100% CPU, leading to Denial-of-Service (CWE-835).",
    "type_mismatch":          "Medium — Implicit type conversions can silently truncate data, changing program behavior in security-relevant ways (CWE-197).",
    "buffer_overflow":        "CRITICAL — Stack/heap buffer overflows can overwrite return addresses or vtable pointers, enabling arbitrary code execution (CWE-120/CWE-787).",
    "use_after_free":         "CRITICAL — Use-after-free allows attackers to control freed memory and redirect execution (CWE-416).",
    "command_injection":      "CRITICAL — Unsanitized input passed to system() gives attackers full OS command execution (CWE-78).",
    "format_string":          "CRITICAL — Format-string bugs allow attackers to read/write arbitrary memory via %n, leading to code execution (CWE-134).",
    "integer_overflow":       "High — Integer overflows cause incorrect size calculations, leading to under-allocated buffers and heap corruption (CWE-190).",
    "invalid_directive":      "Low — Syntax error only; no direct security impact.",
    "missing_main":           "Low — Structural error, program cannot execute.",
    "energy_inefficiency":    "N/A — This is a Green Compiler metric, not a direct security vulnerability. Green Compilers focus on sustainability by flagging energy-draining code.",
}


def get_meta(error_type: str) -> dict:
    """Return severity, category, nature for a given error_type."""
    sev, cat, nat = _META.get(error_type, ("Medium", "Runtime", "Logical"))
    return {
        "severity":   sev,
        "category":   cat,
        "nature":     nat,
        "suggestion": FIX_SUGGESTIONS.get(error_type, "Consult the compiler documentation."),
        "security":   SECURITY_RELEVANCE.get(error_type, "Unknown — refer to OWASP/CWE for guidance."),
    }


# ──────────────────────────────────────────────────────────────────────────────
#  Regex scanner
# ──────────────────────────────────────────────────────────────────────────────

def scan_source(source_text: str) -> list[dict]:
    """
    Scan C++ source text with regex heuristics.
    Returns a list of suspected errors: {line, error_type, message, suggestion, ...}.
    This is a FALLBACK / SUPPLEMENT — Clang output takes priority.
    """
    errors = []
    lines = source_text.splitlines()

    # ── Pre-pass: track nullptr/NULL-assigned pointer variable names ─────────
    # e.g.  int* ptr = nullptr;   →  track 'ptr'
    null_ptr_vars: set[str] = set()
    null_ptr_var_lines: dict[str, int] = {}      # var → line where assigned
    for _ln, _rl in enumerate(lines, start=1):
        _s = re.sub(r"//.*$", "", _rl)
        # int* ptr = nullptr;  OR  ptr = nullptr;
        m = re.search(
            r"(?:int|char|void|auto|\w+)\s*\*+\s*(\w+)\s*=\s*(?:nullptr|NULL)\b"
            r"|\b(\w+)\s*=\s*(?:nullptr|NULL)\b",
            _s
        )
        if m:
            var = m.group(1) or m.group(2)
            if var:
                null_ptr_vars.add(var)
                null_ptr_var_lines[var] = _ln

    # ── Helper: check if a variable is guarded by a null-check ───────────────
    def _is_null_guarded(var: str, current_lineno: int) -> bool:
        """
        Look backward from current_lineno (up to 10 lines) to see if there
        is an enclosing 'if (var != nullptr)' or 'if (var)' guard.
        Stops backward search when it hits a closing '}' (left the guarded block).
        """
        guard_patterns = [
            re.compile(rf"if\s*\(.*\b{re.escape(var)}\b.*!=\s*(?:nullptr|NULL)"),
            re.compile(rf"if\s*\(.*(?:nullptr|NULL)\s*!=.*\b{re.escape(var)}\b"),
            re.compile(rf"if\s*\(\s*{re.escape(var)}\s*\)"),       # if (ptr)
            re.compile(rf"if\s*\(\s*{re.escape(var)}\s*!="),       # if (ptr !=
        ]
        # Search the last 10 lines before current line
        start = max(0, current_lineno - 11)
        for prev_line in reversed(lines[start:current_lineno - 1]):
            clean_prev = re.sub(r"//.*$", "", prev_line)
            for pat in guard_patterns:
                if pat.search(clean_prev):
                    return True
        return False

    # ── Pre-pass: track delete'd pointer variable names ───────────────────────
    # e.g.  delete ptr;  →  track 'ptr'
    deleted_vars: set[str] = set()
    deleted_var_lines: dict[str, int] = {}
    for _ln, _rl in enumerate(lines, start=1):
        _s = re.sub(r"//.*$", "", _rl)
        m = re.search(r"\bdelete\s+(?:\[\]\s*)?(\w+)\s*;", _s)
        if m:
            deleted_vars.add(m.group(1))
            deleted_var_lines[m.group(1)] = _ln

    # ── Per-line checks ──────────────────────────────────────────────────────
    open_braces = 0
    close_braces = 0
    inside_comment = False

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        # Track block comments
        if "/*" in raw_line:
            inside_comment = True
        if "*/" in raw_line:
            inside_comment = False
            continue
        if inside_comment:
            continue

        # Strip single-line comments and mask string literals
        stripped = re.sub(r"//.*$", "", raw_line)
        stripped_masked = re.sub(r'"[^"]*"', '""', stripped)

        # Count braces (from masked version to avoid counting braces in strings)
        open_braces  += stripped_masked.count("{")
        close_braces += stripped_masked.count("}")

        # ── Unterminated string literal ──────────────────────────────────────
        # Check for lines with an odd number of unescaped double-quotes
        # (after removing comment text). Only flag code lines, not preprocessor.
        if not line.startswith("#"):
            _raw_no_comment = re.sub(r"//.*$", "", raw_line)
            # Count non-escaped quotes
            _quote_count = len(re.findall(r'(?<!\\)"', _raw_no_comment))
            if _quote_count % 2 != 0:
                errors.append({
                    "line":       lineno,
                    "error_type": "missing_semicolon",   # closest compile-time syntax category
                    "message":    f"Line {lineno}: Unterminated string literal — missing closing '\"'. "
                                  f"Check for misplaced quotes in the cout/print statement.",
                    **get_meta("missing_semicolon"),
                })

        # Division by zero literal
        if re.search(r"/\s*0\b", stripped_masked) and "/*" not in stripped_masked:
            errors.append({
                "line":       lineno,
                "error_type": "division_by_zero",
                "message":    f"Line {lineno}: Possible division by zero literal detected.",
                **get_meta("division_by_zero"),
            })

        # Assignment inside if/while (= not ==)
        if re.search(r"\bif\s*\([^)]*[^!<>=]\=[^=]", stripped_masked):
            errors.append({
                "line":       lineno,
                "error_type": "assignment_in_condition",
                "message":    f"Line {lineno}: Assignment '=' used inside condition — did you mean '=='?",
                **get_meta("assignment_in_condition"),
            })

        # ── Null pointer dereference (direct: nullptr-> or NULL->) ────────────
        if re.search(r"nullptr\s*->|\bNULL\s*->", stripped_masked):
            errors.append({
                "line":       lineno,
                "error_type": "null_ptr_access",
                "message":    f"Line {lineno}: Direct null pointer dereference via '->' on nullptr/NULL.",
                **get_meta("null_ptr_access"),
            })

        # ── Null pointer dereference (tracked vars: *ptr where ptr=nullptr) ───
        for var in null_ptr_vars:
            assign_line = null_ptr_var_lines.get(var, 0)
            if lineno > assign_line:
                # Check for *var or var-> usage after assignment
                if re.search(rf"(?:\*\s*{re.escape(var)}\b|\b{re.escape(var)}\s*->)", stripped_masked):
                    # Skip if this dereference is inside a proper null guard
                    if not _is_null_guarded(var, lineno):
                        errors.append({
                            "line":       lineno,
                            "error_type": "null_ptr_access",
                            "message":    f"Line {lineno}: Dereferencing null pointer '{var}' (assigned nullptr at line {assign_line}). "
                                          f"This causes a segmentation fault (runtime crash).",
                            **get_meta("null_ptr_access"),
                        })
                    break  # one warning per line (guarded or not)

        # ── Use-after-free (tracked vars: *ptr or ptr-> after delete ptr) ─────
        for var in deleted_vars:
            del_line = deleted_var_lines.get(var, 0)
            if lineno > del_line:
                if re.search(rf"(?:\*\s*{re.escape(var)}\b|\b{re.escape(var)}\s*->|\b{re.escape(var)}\s*\[)", stripped_masked):
                    errors.append({
                        "line":       lineno,
                        "error_type": "use_after_free",
                        "message":    f"Line {lineno}: Use-after-free — '{var}' was deleted at line {del_line} "
                                      f"but is accessed again here. This is undefined behavior (CWE-416).",
                        **get_meta("use_after_free"),
                    })
                    break  # one warning per line

        # Dangerous functions — detected on raw (unmasked) stripped line
        # so they are found even when #include <cstring> is missing
        dangerous = {
            "gets":    ("buffer_overflow", "Unsafe function 'gets()' — use fgets() instead. Requires #include <cstring>."),
            "strcpy":  ("buffer_overflow", "Unsafe function 'strcpy()' — use strncpy() or std::string. Requires #include <cstring>."),
            "strcat":  ("buffer_overflow", "Unsafe function 'strcat()' — use strncat() or std::string. Requires #include <cstring>."),
            "sprintf": ("buffer_overflow", "Unsafe function 'sprintf()' — use snprintf() instead. Requires #include <cstdio>."),
            "system":  ("command_injection", "Function 'system()' with unsanitized input risks command injection (CWE-78)."),
            "popen":   ("command_injection", "Function 'popen()' risks command injection — sanitize arguments carefully."),
        }
        for fn, (etype, msg) in dangerous.items():
            if re.search(rf"\b{fn}\s*\(", stripped):  # use unmasked stripped
                errors.append({
                    "line":       lineno,
                    "error_type": etype,
                    "message":    f"Line {lineno}: {msg}",
                    **get_meta(etype),
                })

        # printf with non-literal format string
        if re.search(r"\bprintf\s*\(\s*[^\"']", stripped_masked):
            errors.append({
                "line":       lineno,
                "error_type": "format_string",
                "message":    f"Line {lineno}: printf() called with non-literal format string — potential format-string vulnerability.",
                **get_meta("format_string"),
            })

        # Integer overflow: arithmetic on INT_MAX / INT_MIN / LONG_MAX etc.
        if re.search(r"\b(INT_MAX|INT_MIN|LONG_MAX|LONG_MIN|UINT_MAX|SHRT_MAX)\s*[+\-\*]", stripped_masked) or \
           re.search(r"[+\-\*]\s*(INT_MAX|INT_MIN|LONG_MAX|LONG_MIN|UINT_MAX|SHRT_MAX)\b", stripped_masked):
            errors.append({
                "line":       lineno,
                "error_type": "integer_overflow",
                "message":    f"Line {lineno}: Arithmetic on INT_MAX/INT_MIN detected — this causes signed integer overflow (Undefined Behavior in C++).",
                **get_meta("integer_overflow"),
            })

    # ── Whole-file checks ────────────────────────────────────────────────────

    # Brace mismatch
    if open_braces != close_braces:
        errors.append({
            "line":       1,
            "error_type": "missing_brace",
            "message":    f"Brace mismatch: {open_braces} opening '{{' vs {close_braces} closing '}}' braces.",
            **get_meta("missing_brace"),
        })

    # Missing main
    if not re.search(r"\bint\s+main\s*\(", source_text) and not re.search(r"\bvoid\s+main\s*\(", source_text):
        errors.append({
            "line":       1,
            "error_type": "missing_main",
            "message":    "Missing 'int main()' entry point function.",
            **get_meta("missing_main"),
        })

    return errors


def scan_infinite_loops(source_text: str) -> list[dict]:
    """
    Heuristic scan for infinite loop patterns in source text.
    Returns errors list (may be empty).
    """
    errors = []
    lines = source_text.splitlines()
    has_any_exit = bool(re.search(r"\b(break|return|exit)\s*[\(;]", source_text))

    for lineno, raw_line in enumerate(lines, start=1):
        stripped = re.sub(r"//.*$", "", raw_line)
        # while(true) or while(1) or for(;;) without any exit in file
        if re.search(r"\bwhile\s*\(\s*(true|1)\s*\)|\bfor\s*\(\s*;\s*;\s*\)", stripped):
            if not has_any_exit:
                errors.append({
                    "line":       lineno,
                    "error_type": "infinite_loop",
                    "message":    f"Line {lineno}: Potential infinite loop — no break/return/exit found in function.",
                    **get_meta("infinite_loop"),
                })
            break   # one warning per loop-type finding is enough

    return errors
