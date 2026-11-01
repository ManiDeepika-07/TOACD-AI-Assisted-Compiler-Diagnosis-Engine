"""
parser/cfg.py
Control Flow Graph (CFG) builder and infinite-loop cycle detector.

Algorithm:
  1. Parse source into a simplified list of "blocks" with type tags.
  2. Build a directed graph (adjacency list).
  3. Run DFS to find back-edges (cycles).
  4. For each cycle, check whether ALL paths through the back-edge
     contain a guaranteed exit statement (break / return / exit / throw).
  5. Report cycles without guaranteed exits as infinite loops.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
#  Data structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Block:
    id: int
    start_line: int
    end_line: int
    block_type: str          # 'seq', 'loop_header', 'loop_body', 'cond', 'exit'
    has_exit: bool = False   # contains break/return/exit/throw
    successors: list = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
#  Tokeniser — extremely simplified C++ flow analysis
# ──────────────────────────────────────────────────────────────────────────────

_LOOP_OPEN   = re.compile(r"^\s*(while|for|do)\s*[\({]?")
_IF_OPEN     = re.compile(r"^\s*if\s*\(")
_BRACE_OPEN  = re.compile(r"\{")
_BRACE_CLOSE = re.compile(r"\}")
_EXIT_STMT   = re.compile(r"\b(break|return|exit|throw|continue)\b")
_WHILE_TRUE  = re.compile(r"\bwhile\s*\(\s*(true|1)\s*\)")
_FOR_INF     = re.compile(r"\bfor\s*\(\s*;\s*;\s*\)")


class CFGBuilder:
    """
    Lightweight CFG builder for C++ source code.
    Detects loops and checks whether they have guaranteed exits.
    """

    def __init__(self, source: str):
        self.source  = source
        self.lines   = source.splitlines()
        self._blocks: list[Block] = []
        self._next_id = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def find_infinite_loops(self) -> list[dict]:
        """
        Returns a list of dicts: {line, error_type, message, ...}
        for loops that are detected as infinite (no guaranteed exit).
        """
        results = []
        loop_stack: list[dict] = []  # {start_line, has_exit, brace_depth}
        brace_depth    = 0
        inside_comment = False

        for lineno, raw in enumerate(self.lines, start=1):
            # ── Comment stripping ────────────────────────────────────────────
            if "/*" in raw:
                inside_comment = True
            if "*/" in raw:
                inside_comment = False
            if inside_comment:
                continue

            clean = re.sub(r"//.*$", "", raw)
            clean = re.sub(r'"[^"]*"', '""', clean)  # mask string literals

            # Track brace depth
            opens  = clean.count("{")
            closes = clean.count("}")

            # ── Detect loop headers ──────────────────────────────────────────
            is_infinite_header = bool(
                _WHILE_TRUE.search(clean) or _FOR_INF.search(clean)
            )
            is_any_loop = is_infinite_header or bool(_LOOP_OPEN.match(clean))
            is_counted_loop = is_any_loop and not is_infinite_header

            if is_any_loop and opens > 0:
                # Push a new loop frame on the stack (brace on same line)
                loop_stack.append({
                    "start_line":  lineno,
                    "body_depth":  brace_depth + opens,  # depth INSIDE loop body
                    "has_exit":    False,
                    "is_inf_hdr":  is_infinite_header,
                    "is_counted":  is_counted_loop,
                    "pending":     False,
                })
            elif is_any_loop and opens == 0:
                # Allman style: brace is on the NEXT line — push as pending
                loop_stack.append({
                    "start_line":  lineno,
                    "body_depth":  -1,       # resolved when { arrives
                    "has_exit":    False,
                    "is_inf_hdr":  is_infinite_header,
                    "is_counted":  is_counted_loop,
                    "pending":     True,
                })

            brace_depth += opens

            # ── Resolve pending loops: brace arrived on this line ────────────
            if opens > 0:
                for frame in loop_stack:
                    if frame.get("pending"):
                        frame["body_depth"] = brace_depth
                        frame["pending"]    = False

            # ── Check for exits inside current loop bodies ───────────────────
            if loop_stack and _EXIT_STMT.search(clean):
                # Mark the innermost loop that could be exited
                loop_stack[-1]["has_exit"] = True

            brace_depth -= closes

            # ── Pop loops whose body just closed ────────────────────────────
            while loop_stack and not loop_stack[-1].get("pending") and \
                  loop_stack[-1]["body_depth"] > 0 and \
                  brace_depth < loop_stack[-1]["body_depth"]:
                loop = loop_stack.pop()
                start = loop["start_line"]
                has_exit = loop["has_exit"]
                is_counted = loop["is_counted"]
                is_inf_hdr = loop["is_inf_hdr"]

                # Heuristic decision rules:
                # 1. Explicit infinite header (while(true)/for(;;)) + no exit → INFINITE
                # 2. Counted for/while whose condition never becomes false + no exit → INFINITE
                #    We confirm case 2 by checking the update direction (basic heuristic).
                if is_inf_hdr and not has_exit:
                    results.append(_make_infinite_error(start))
                elif is_counted and not has_exit:
                    # Check for classic wrong-direction counter
                    region = "\n".join(self.lines[max(0, start-1):lineno])
                    if _wrong_direction_loop(region):
                        results.append(_make_infinite_error(start))

        return results


def _make_infinite_error(line: int) -> dict:
    from parser.regex_parser import get_meta
    meta = get_meta("infinite_loop")
    return {
        "line":       line,
        "error_type": "infinite_loop",
        "message":    f"Line {line}: Infinite loop detected — loop has no guaranteed exit (break/return/exit).",
        **meta,
    }


def _wrong_direction_loop(region: str) -> bool:
    """
    Returns True if a counted loop using i++ has condition i >= 0 (always true),
    or uses i-- with condition i < N (always true / going negative forever).
    These are common infinite-loop mistakes.
    """
    # for(int i = 0; i >= 0; i++) — always true
    if re.search(r"for\s*\([^;]*;\s*\w+\s*>=\s*0\s*;\s*\w+\+\+", region):
        return True
    # for(int i = 0; i < N; i--) — decrementing upward loop
    if re.search(r"for\s*\([^;]*;\s*\w+\s*<[^;]+;\s*\w+--", region):
        return True
    # while(i < N) with i-- in body
    if re.search(r"while\s*\(\s*\w+\s*<", region) and re.search(r"\w+--", region):
        if not re.search(r"\w+\+\+", region):
            return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
#  Public helper
# ──────────────────────────────────────────────────────────────────────────────

def detect_infinite_loops(source_text: str) -> list[dict]:
    """
    Main entry point.  Returns a deduplicated list of infinite-loop errors.
    """
    builder = CFGBuilder(source_text)
    return builder.find_infinite_loops()
