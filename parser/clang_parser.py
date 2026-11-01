"""
parser/clang_parser.py
Multi-error aware Clang AST + stderr parser.
Returns a list of individual error dicts, one per Clang diagnostic.
"""
import subprocess
import re
import os


# ──────────────────────────────────────────────────────────────────────────────
#  Clang invocation
# ──────────────────────────────────────────────────────────────────────────────

def run_clang(file_path: str):
    """
    Run clang -fsyntax-only -Wall -Wextra and return (stdout_ast, stderr_text).
    stdout_ast is the AST dump; stderr_text contains all diagnostics.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # mock_inc lives one level up (in scripts/)
    mock_inc = os.path.join(script_dir, "..", "mock_inc")
    mock_inc = os.path.normpath(mock_inc)

    try:
        # Phase 1: AST dump
        ast_result = subprocess.run(
            ["clang", "-Xclang", "-ast-dump", "-fsyntax-only",
             "-Wall", "-Wextra", "-I", mock_inc, file_path],
            capture_output=True, text=True, check=False, timeout=30
        )
        # Phase 2: plain diagnostics (separate run for cleaner stderr)
        diag_result = subprocess.run(
            ["clang", "-fsyntax-only", "-Wall", "-Wextra",
             "-I", mock_inc, file_path],
            capture_output=True, text=True, check=False, timeout=30
        )
        return ast_result.stdout, diag_result.stderr
    except FileNotFoundError:
        # clang not on PATH — return empty
        return "", ""
    except subprocess.TimeoutExpired:
        return "", "error: compilation timed out"
    except Exception as exc:
        return "", str(exc)


# ──────────────────────────────────────────────────────────────────────────────
#  Clang stderr → list of error dicts
# ──────────────────────────────────────────────────────────────────────────────

# Clang diagnostic pattern:  file.cpp:line:col: error/warning: message
_DIAG_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):\s*"
    r"(?P<level>error|warning|note):\s*(?P<msg>.+)$",
    re.MULTILINE,
)

# ── Error message → internal error_type ───────────────────────────────────────
_MSG_TO_TYPE = [
    # Syntax
    (re.compile(r"invalid preprocessing directive", re.I), "invalid_directive"),
    (re.compile(r"expected\s*'[;]'|missing\s*';'", re.I),          "missing_semicolon"),
    (re.compile(r"expected\s*'[{}]'|missing\s*'[{}]'", re.I),      "missing_brace"),
    (re.compile(r"use of undeclared|was not declared|undeclared", re.I), "undeclared_variable"),
    # Type
    (re.compile(r"cannot initialize|no viable conversion|invalid conversion|cannot convert|incompatible type", re.I), "type_mismatch"),
    (re.compile(r"narrowing conversion|implicit conversion.*loses", re.I), "type_mismatch"),
    (re.compile(r"void.*return.*value|return.*void", re.I),         "type_mismatch"),
    # Memory / runtime
    (re.compile(r"uninitialized|may be used uninitialized", re.I),  "uninitialized_variable"),
    (re.compile(r"division by zero|divide by zero", re.I),          "division_by_zero"),
    (re.compile(r"null pointer|null dereference", re.I),            "null_ptr_access"),
    # Security
    (re.compile(r"deprecated.*gets|'gets'.*unsafe", re.I),          "buffer_overflow"),
    (re.compile(r"buffer.*overflow|stack.*smash", re.I),            "buffer_overflow"),
    (re.compile(r"array index|past the end of the array|-warray-bounds", re.I), "out_of_bounds"),
]


def _classify_clang_message(msg: str) -> str:
    """Map a raw Clang message string to an internal error_type."""
    for pattern, etype in _MSG_TO_TYPE:
        if pattern.search(msg):
            return etype
    return "unknown"


def parse_clang_errors(stderr_text: str, source_text: str = "") -> list[dict]:
    """
    Parse ALL error/warning lines from clang stderr.
    Returns a list of dicts:  {line, col, level, message, error_type}
    """
    results = []
    seen = set()  # deduplicate (same line+type)

    for m in _DIAG_RE.finditer(stderr_text):
        level = m.group("level")
        if level == "note":
            continue  # skip note continuations
        line_no = int(m.group("line"))
        msg = m.group("msg").strip()
        etype = _classify_clang_message(msg)

        key = (line_no, etype, level)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "line":       line_no,
            "col":        int(m.group("col")),
            "level":      level,
            "message":    msg,
            "error_type": etype,
        })

    return results


# ──────────────────────────────────────────────────────────────────────────────
#  Aggregate stderr feature flags (used by the ML model)
# ──────────────────────────────────────────────────────────────────────────────

def extract_stderr_features(stderr_text: str) -> dict:
    """Return a flat dict of 0/1 features from Clang stderr output."""
    t = stderr_text.lower()
    error_lines   = [l for l in stderr_text.splitlines()
                     if " error:" in l and "file not found" not in l.lower()]
    warning_lines = [l for l in stderr_text.splitlines() if " warning:" in l]

    return {
        "stderr_has_error":           int(len(error_lines) > 0),
        "stderr_has_warning":         int(len(warning_lines) > 0),
        "stderr_error_count":         len(error_lines),
        "stderr_warning_count":       len(warning_lines),
        "stderr_missing_brace":       int("expected '}'" in t or "missing '}'" in t or "expected '{'" in t),
        "stderr_missing_semi":        int("expected ';'" in t or "missing semicolon" in t),
        "stderr_expected_expr":       int("expected expression" in t),
        "stderr_undeclared":          int("undeclared" in t or "was not declared" in t),
        "stderr_type_mismatch":       int(any(p in t for p in [
                                         "cannot initialize","incompatible","cannot convert",
                                         "no viable conversion","invalid conversion"])),
        "stderr_implicit_narrowing":  int("implicit conversion" in t or "narrowing conversion" in t
                                         or "loses precision" in t),
        "stderr_void_return":         int("void" in t and "return" in t and
                                         ("value" in t or "expression" in t)),
        "stderr_return_type":         int("return type" in t),
        "stderr_null_deref":          int("null pointer" in t or "null dereference" in t),
        "stderr_uninit":              int("uninitialized" in t or "may be used uninitialized" in t),
        "stderr_div_zero":            int("division by zero" in t or "divide by zero" in t),
        "stderr_deprecated":          int("deprecated" in t or "insecure" in t),
        "stderr_format_security":     int("-wformat-security" in t or "format string is not a string literal" in t),
        "stderr_buffer":              int("-warray-bounds" in t or "array index out of bounds" in t or "past the end of the array" in t),
    }


# ──────────────────────────────────────────────────────────────────────────────
#  AST structural feature extraction
# ──────────────────────────────────────────────────────────────────────────────

_NODE_RE = re.compile(
    r"([A-Za-z]+Decl|[A-Za-z]+Expr|CompoundStmt|BinaryOperator|UnaryOperator|"
    r"ReturnStmt|ForStmt|WhileStmt|DoStmt|IfStmt|CallExpr|IntegerLiteral|"
    r"BreakStmt|ContinueStmt|GotoStmt|CStyleCastExpr|ImplicitCastExpr|"
    r"CXXReinterpretCastExpr|CXXStaticCastExpr|FloatingLiteral|StringLiteral)"
)


def extract_ast_features(ast_text: str, source_text: str = "") -> dict:
    """Extract structural/loop/security features from Clang AST dump text."""
    features = {
        "node_counts": {},
        "depth_max": 0,
        "max_loop_nesting": 0,
        "total_nodes": 0,
        "uninit_vars": 0,
        "null_ptrs": 0,
        "has_while_true": 0,
        "loop_without_exit": 0,
        "loop_exit_count": 0,
        "implicit_cast_count": 0,
        "cstyle_cast_count": 0,
        "reinterpret_cast_count": 0,
        "strcpy_call": 0,
        "gets_call": 0,
        "sprintf_call": 0,
        "system_call": 0,
        "malloc_call": 0,
        "free_call": 0,
        "printf_userctrl": 0,
    }

    lines = ast_text.split("\n")
    loop_stack = []

    for i, line in enumerate(lines):
        m = _NODE_RE.search(line)
        if not m:
            continue
        node_type = m.group(1)
        
        depth = (len(line) - len(line.lstrip("| `-"))) // 2
        
        while loop_stack and loop_stack[-1] >= depth:
            loop_stack.pop()

        features["total_nodes"] += 1
        nc = features["node_counts"]
        nc[node_type] = nc.get(node_type, 0) + 1

        features["depth_max"] = max(features["depth_max"], depth)

        if node_type == "BinaryOperator":
            op_m = re.search(r"'([^']+)'\s*$", line)
            if op_m:
                op = op_m.group(1)
                nc[f"op_{op}"] = nc.get(f"op_{op}", 0) + 1

        if node_type == "UnaryOperator":
            op = "++" if "++" in line else ("--" if "--" in line else "other")
            nc[f"uop_{op}"] = nc.get(f"uop_{op}", 0) + 1

        if node_type == "VarDecl" and "col:" in line and "cinit" not in line:
            indent = line[: len(line) - len(line.lstrip("| `-"))]
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if not next_line.startswith(indent + "  "):
                features["uninit_vars"] += 1

        if "nullptr" in line or (" 0 " in line and "Expr" in line):
            features["null_ptrs"] += 1

        if node_type == "ImplicitCastExpr":
            features["implicit_cast_count"] += 1
        if node_type == "CStyleCastExpr":
            features["cstyle_cast_count"] += 1
        if node_type == "CXXReinterpretCastExpr":
            features["reinterpret_cast_count"] += 1

        if node_type in ("ForStmt", "WhileStmt", "DoStmt"):
            if re.search(r"while\s*\(\s*(true|1)\s*\)", line):
                features["has_while_true"] += 1
            loop_stack.append(depth)
            features["max_loop_nesting"] = max(features["max_loop_nesting"], len(loop_stack))

        if node_type in ("BreakStmt", "ReturnStmt") and loop_stack:
            features["loop_exit_count"] += 1

        if node_type == "CallExpr":
            func_m = re.search(r"'([a-zA-Z_][a-zA-Z0-9_]*)'\s*'", line)
            if func_m:
                fname = func_m.group(1)
                key = f"{fname}_call"
                if key in features:
                    features[key] += 1

    # Source-level heuristics
    if source_text:
        has_inf = bool(
            re.search(r"while\s*\(\s*(true|1)\s*\)", source_text) or
            re.search(r"for\s*\(\s*;\s*;\s*\)", source_text)
        )
        has_exit = bool(re.search(r"\b(break|return|exit)\s*[\(;]", source_text))
        if has_inf and features["loop_exit_count"] == 0:
            features["loop_without_exit"] = 1

        for fn in ("strcpy", "strcat", "gets", "sprintf", "system", "popen", "malloc", "free"):
            if re.search(rf"\b{fn}\s*\(", source_text):
                key = f"{fn}_call"
                if key in features:
                    features[key] = max(features[key], 1)

        if re.search(r"printf\s*\(\s*[^\"']\w", source_text):
            features["printf_userctrl"] = 1

    # Static Green Analysis Heuristic
    features["energy_inefficient"] = 1 if features["max_loop_nesting"] >= 3 else 0

    return features
