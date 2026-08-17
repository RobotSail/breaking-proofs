#!/usr/bin/env python3
"""Eval harness for breaking-proofs.

Dimensions:
  oracle_correctness (0.35): oracle regression tests
  cross_check_parity (0.20): galois vs reference oracle agreement
  tests (0.15): full test suite
  lint (0.10): ruff check
  type_check (0.10): py_compile on all source files
  observability (0.10): structured logging coverage

Output format:
    {"results": [{"name": str, "score": float, "weight": float, "passed": bool, "details": str}, ...]}
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _pytest_score(test_args: list[str], timeout: int = 300) -> tuple[float, bool, str]:
    try:
        result = _run(["python", "-m", "pytest", *test_args, "-v", "--tb=short"], timeout)
        output = result.stdout + result.stderr
        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        error_match = re.search(r"(\d+) error", output)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        total = passed + failed + errors

        if total == 0:
            return 0.0, False, "No tests collected"

        score = passed / total
        return score, result.returncode == 0, output.strip()[-500:]
    except subprocess.TimeoutExpired:
        return 0.0, False, "Timed out"
    except FileNotFoundError:
        return 0.0, False, "pytest not found"


def eval_oracle_correctness() -> dict:
    score, ok, details = _pytest_score(
        ["tests/test_oracle_small.py", "tests/test_kkh26.py"],
        timeout=300,
    )
    return {
        "name": "oracle_correctness",
        "score": round(score, 3),
        "weight": 0.35,
        "passed": ok,
        "details": details,
    }


def eval_cross_check_parity() -> dict:
    score, ok, details = _pytest_score(
        ["tests/test_oracle_cross_check.py"],
        timeout=300,
    )
    return {
        "name": "cross_check_parity",
        "score": round(score, 3),
        "weight": 0.20,
        "passed": ok,
        "details": details,
    }


def eval_tests() -> dict:
    score, ok, details = _pytest_score(["tests/"], timeout=300)
    return {
        "name": "tests",
        "score": round(score, 3),
        "weight": 0.15,
        "passed": ok,
        "details": details,
    }


def eval_lint() -> dict:
    try:
        result = _run(["python", "-m", "ruff", "check", "src/", "tests/"], timeout=60)
        output = (result.stdout + result.stderr).strip()
        if result.returncode == 0:
            return {
                "name": "lint",
                "score": 1.0,
                "weight": 0.10,
                "passed": True,
                "details": "Clean",
            }

        error_lines = [ln for ln in output.splitlines() if ln.strip() and ":" in ln]
        score = max(0.0, 1.0 - len(error_lines) * 0.05)
        return {
            "name": "lint",
            "score": round(score, 3),
            "weight": 0.10,
            "passed": False,
            "details": output[-500:],
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {
            "name": "lint",
            "score": 0.0,
            "weight": 0.10,
            "passed": False,
            "details": str(e),
        }


def eval_type_check() -> dict:
    src_files = list(Path("src").rglob("*.py"))
    if not src_files:
        return {
            "name": "type_check",
            "score": 0.0,
            "weight": 0.10,
            "passed": False,
            "details": "No source files found",
        }

    passed = 0
    errors = []
    for f in src_files:
        try:
            result = _run(["python", "-m", "py_compile", str(f)], timeout=30)
            if result.returncode == 0:
                passed += 1
            else:
                errors.append(f"{f}: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            errors.append(f"{f}: timeout")

    score = passed / len(src_files) if src_files else 0.0
    details = f"{passed}/{len(src_files)} files OK"
    if errors:
        details += "; " + "; ".join(errors[:5])

    return {
        "name": "type_check",
        "score": round(score, 3),
        "weight": 0.10,
        "passed": len(errors) == 0,
        "details": details,
    }


def eval_observability() -> dict:
    skip = {
        "tests", "test", ".venv", "venv", "node_modules", "__pycache__",
        ".git", ".factory", "eval", "dist", "build", ".mypy_cache",
    }
    log_pats = [
        r"\blogger\.\w+\(",
        r"\blogging\.\w+\(",
        r"\blog\.\w+\(",
    ]
    struct_pats = [r"\bstructlog\b"]
    trace_pats = [r"\bcontextvars\b|ContextVar"]

    sources = [f for f in Path(".").rglob("*.py")
               if not any(p in f.parts for p in skip)]
    total_fn = logged_fn = total_log = 0
    has_struct = has_trace = False

    for src in sources:
        try:
            code = src.read_text(errors="replace")
        except OSError:
            continue
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        lines = code.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("__"):
                    continue
                total_fn += 1
                start = node.lineno - 1
                end = node.end_lineno or start + 1
                body = "\n".join(lines[start:end])
                for pat in log_pats:
                    if re.search(pat, body):
                        logged_fn += 1
                        break
        for pat in log_pats:
            total_log += len(re.findall(pat, code))
        for pat in struct_pats:
            if re.search(pat, code):
                has_struct = True
        for pat in trace_pats:
            if re.search(pat, code, re.IGNORECASE):
                has_trace = True

    if total_fn == 0:
        return {"name": "observability", "score": 0.0, "weight": 0.10,
                "passed": True, "details": "No functions found to analyze"}

    cov = logged_fn / total_fn
    density = min(1.0, total_log / max(total_fn, 1))
    score = 0.40 * cov + 0.25 * float(has_struct) + 0.20 * float(has_trace) + 0.15 * density

    details = (f"coverage={cov:.0%} ({logged_fn}/{total_fn}), "
               f"structured={'yes' if has_struct else 'no'}, "
               f"tracing={'yes' if has_trace else 'no'}, "
               f"density={density:.0%}")

    return {"name": "observability", "score": round(score, 3), "weight": 0.10,
            "passed": score >= 0.3, "details": details}


EVALS = [
    eval_oracle_correctness,
    eval_cross_check_parity,
    eval_tests,
    eval_lint,
    eval_type_check,
    eval_observability,
]


def main() -> None:
    results = [fn() for fn in EVALS]
    output = {"results": results}
    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
