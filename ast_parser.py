import subprocess
import json
import re
import os


import shutil

def get_clang_executable() -> str:
    p = shutil.which("clang")
    if p:
        return p
    candidates = [
        r"C:\Program Files\LLVM\bin\clang.exe",
        r"C:\Program Files (x86)\LLVM\bin\clang.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\LLVM\bin\clang.exe"),
        "/usr/bin/clang",
        "/usr/local/bin/clang",
        "/opt/homebrew/bin/clang"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "clang"


def get_ast_dump(file_path):
    """Runs clang -Xclang -ast-dump -fsyntax-only and returns stdout, stderr."""
    try:
        # Resolve mock_inc relative to this script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mock_inc = os.path.join(script_dir, "mock_inc")
        clang_bin = get_clang_executable()
        
        result = subprocess.run(
            [clang_bin, "-Xclang", "-ast-dump", "-fsyntax-only", "-Wall", "-Wextra", "-I", mock_inc, file_path],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)


def parse_ast_line(line):
    """Extract the primary AST node type from a single clang dump line."""
    match = re.search(
        r'([A-Za-z]+Decl|[A-Za-z]+Expr|CompoundStmt|BinaryOperator|UnaryOperator|'
        r'ReturnStmt|ForStmt|WhileStmt|DoStmt|IfStmt|CallExpr|IntegerLiteral|'
        r'BreakStmt|ContinueStmt|GotoStmt|CStyleCastExpr|ImplicitCastExpr|'
        r'CXXReinterpretCastExpr|CXXStaticCastExpr|FloatingLiteral|StringLiteral)',
        line
    )
    return match.group(1) if match else None


# ─────────────────────────────────────────────────────────────────────────────
#  STDERR FEATURE EXTRACTION  (Clang's actual diagnostics → numeric flags)
# ─────────────────────────────────────────────────────────────────────────────
def extract_stderr_features(stderr_text: str) -> dict:
    """
    Parse Clang's stderr output into numeric diagnostic features.
    These are far more discriminative than AST structure alone.
    """
    t = stderr_text.lower()

    # Count raw error / warning lines (ignore missing headers like iostream)
    error_lines   = [l for l in stderr_text.splitlines() if ' error:' in l and 'file not found' not in l.lower()]
    warning_lines = [l for l in stderr_text.splitlines() if ' warning:' in l]

    return {
        # ── Generic ─────────────────────────────────────────────────────
        "stderr_has_error":          int(len(error_lines) > 0),
        "stderr_has_warning":        int(len(warning_lines) > 0),
        "stderr_error_count":        len(error_lines),
        "stderr_warning_count":      len(warning_lines),

        # ── Syntax / brace / semicolon ───────────────────────────────────
        "stderr_missing_brace":      int("expected '}'" in t or
                                         "missing '}'" in t or
                                         "expected '{'" in t),
        "stderr_missing_semi":       int("expected ';'" in t or
                                         "missing semicolon" in t),
        "stderr_expected_expr":      int("expected expression" in t),
        "stderr_undeclared":         int("undeclared" in t or
                                         "was not declared" in t or
                                         "use of undeclared" in t),

        # ── Type issues ──────────────────────────────────────────────────
        "stderr_type_mismatch":      int("cannot initialize" in t or
                                         "incompatible" in t or
                                         "cannot convert" in t or
                                         "no viable conversion" in t or
                                         "invalid conversion" in t or
                                         "initializing" in t and "type" in t),
        "stderr_implicit_narrowing": int("implicit conversion" in t or
                                         "narrowing conversion" in t or
                                         "loses precision" in t or
                                         "signed" in t and "unsigned" in t),
        "stderr_void_return":        int("void" in t and "return" in t and
                                         ("value" in t or "expression" in t)),
        "stderr_return_type":        int("return type" in t),

        # ── Memory / pointer ────────────────────────────────────────────
        "stderr_null_deref":         int("null pointer" in t or
                                         "null dereference" in t),
        "stderr_uninit":             int("uninitialized" in t or
                                         "may be used uninitialized" in t),
        "stderr_div_zero":           int("division by zero" in t or
                                         "divide by zero" in t),

        # ── Security / dangerous functions ──────────────────────────────
        "stderr_deprecated":         int("deprecated" in t or
                                         "insecure" in t),
        "stderr_format_security":    int("-wformat-security" in t or
                                         "format string is not a string literal" in t),
        "stderr_buffer":             int("-warray-bounds" in t or
                                         "array index out of bounds" in t or
                                         "past the end of the array" in t),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
def extract_features(ast_text, source_text="", stderr_text=""):
    """
    Extract rich structural, loop-exit, security and compiler-diagnostic
    features from a Clang AST dump + optional source text + Clang stderr.
    """
    features = {
        "node_counts": {},
        "depth_max": 0,
        "max_loop_nesting": 0,
        "total_nodes": 0,
        "uninit_vars": 0,
        "null_ptrs": 0,
        # Infinite-loop heuristics
        "has_while_true": 0,
        "loop_without_exit": 0,
        "loop_exit_count": 0,
        # Type-mismatch heuristics
        "implicit_cast_count": 0,
        "cstyle_cast_count": 0,
        "reinterpret_cast_count": 0,
        # Security heuristics
        "strcpy_call": 0,
        "gets_call": 0,
        "sprintf_call": 0,
        "system_call": 0,
        "malloc_call": 0,
        "free_call": 0,
        "printf_userctrl": 0,
    }

    # ── Merge in stderr diagnostic features ──────────────────────────────────
    features.update(extract_stderr_features(stderr_text))

    lines = ast_text.split('\n')
    loop_stack = []

    for i, line in enumerate(lines):
        node_type = parse_ast_line(line)
        if not node_type:
            continue

        depth = (len(line) - len(line.lstrip('| `-'))) // 2
        
        while loop_stack and loop_stack[-1] >= depth:
            loop_stack.pop()

        features["total_nodes"] += 1
        features["node_counts"][node_type] = \
            features["node_counts"].get(node_type, 0) + 1

        features["depth_max"] = max(features["depth_max"], depth)

        # BinaryOperator operator type
        if node_type == 'BinaryOperator':
            op_match = re.search(r"'([^']+)'\s*$", line)
            if op_match:
                op = op_match.group(1)
                features["node_counts"][f"op_{op}"] = \
                    features["node_counts"].get(f"op_{op}", 0) + 1

        # UnaryOperator ++ / --
        if node_type == 'UnaryOperator':
            op = '++' if '++' in line else ('--' if '--' in line else 'other')
            features["node_counts"][f"uop_{op}"] = \
                features["node_counts"].get(f"uop_{op}", 0) + 1

        # Uninitialized variable heuristic
        if node_type == 'VarDecl' and 'col:' in line and 'cinit' not in line:
            indent = line[:len(line) - len(line.lstrip('| `-'))]
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if not next_line.startswith(indent + "  "):
                features["uninit_vars"] += 1

        # Null pointer heuristic
        if 'nullptr' in line or (' 0 ' in line and 'Expr' in line):
            features["null_ptrs"] += 1

        # Cast detection
        if node_type == 'ImplicitCastExpr':
            features["implicit_cast_count"] += 1
        if node_type == 'CStyleCastExpr':
            features["cstyle_cast_count"] += 1
        if node_type == 'CXXReinterpretCastExpr':
            features["reinterpret_cast_count"] += 1

        # Loop / exit tracking
        if node_type in ('ForStmt', 'WhileStmt', 'DoStmt'):
            if re.search(r'while\s*\(\s*(true|1)\s*\)', line):
                features["has_while_true"] += 1
            loop_stack.append(depth)
            features["max_loop_nesting"] = max(features["max_loop_nesting"], len(loop_stack))

        if node_type in ('BreakStmt', 'ReturnStmt'):
            if loop_stack:
                features["loop_exit_count"] += 1

        # Security: dangerous function calls
        if node_type == 'CallExpr':
            func_match = re.search(r"'([a-zA-Z_][a-zA-Z0-9_]*)'\s*'", line)
            if func_match:
                fname = func_match.group(1)
                key = f"{fname}_call"
                if key in features:
                    features[key] += 1

    # ── Source-level heuristics ───────────────────────────────────────────────
    if source_text:
        has_inf = bool(
            re.search(r'while\s*\(\s*(true|1)\s*\)', source_text) or
            re.search(r'for\s*\(\s*;\s*;\s*\)', source_text)
        )
        if has_inf and features["loop_exit_count"] == 0:
            features["loop_without_exit"] = 1

        for fn in ('strcpy', 'strcat', 'gets', 'sprintf', 'system', 'popen', 'malloc', 'free'):
            if re.search(rf'\b{fn}\s*\(', source_text):
                key = f"{fn}_call"
                if key in features:
                    features[key] = max(features[key], 1)

        if re.search(r'printf\s*\(\s*[^"\']\w', source_text):
            features["printf_userctrl"] = 1

    # Static Green Analysis Heuristic: deeply nested structures are energy inefficient
    features["energy_inefficient"] = 1 if features["max_loop_nesting"] >= 3 else 0

    return features


def main():
    data_dir = "data"
    for filename in os.listdir(data_dir):
        if filename.endswith(".cpp"):
            path = os.path.join(data_dir, filename)
            print(f"Analyzing {filename}...")
            stdout, stderr = get_ast_dump(path)
            with open(f"data/{filename}.ast.txt", "w") as f:
                f.write(stdout)
            with open(path) as src:
                source = src.read()
            features = extract_features(stdout, source, stderr)
            print(f"Features: {json.dumps(features, indent=2)}")
            print("-" * 20)


if __name__ == "__main__":
    main()
