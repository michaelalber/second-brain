#!/usr/bin/env python3
"""
Quality gate check for Python projects.
Runs: ruff, mypy, radon (complexity/maintainability), coverage, bandit.
Exit code 0 = all gates pass, non-zero = failure.
"""
import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QualityResult:
    name: str
    passed: bool
    message: str


def run_cmd(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=capture, text=True)


def check_ruff(path: Path) -> QualityResult:
    """Run ruff lint and format check."""
    lint = run_cmd(["ruff", "check", str(path)])
    fmt = run_cmd(["ruff", "format", "--check", str(path)])

    if lint.returncode == 0 and fmt.returncode == 0:
        return QualityResult("Ruff", True, "Lint and format OK")

    msg = []
    if lint.returncode != 0:
        msg.append(f"Lint errors:\n{lint.stdout}")
    if fmt.returncode != 0:
        msg.append("Format check failed")
    return QualityResult("Ruff", False, "\n".join(msg))


def check_mypy(path: Path) -> QualityResult:
    """Run mypy with strict mode."""
    result = run_cmd(["mypy", "--strict", str(path)])
    if result.returncode == 0:
        return QualityResult("mypy", True, "Type check OK")
    return QualityResult("mypy", False, result.stdout)


def check_complexity(path: Path, max_cc: int = 10) -> QualityResult:
    """Check cyclomatic complexity with radon."""
    result = run_cmd(["radon", "cc", "-a", "-s", str(path)])
    if result.returncode != 0:
        return QualityResult("Complexity", False, f"radon failed: {result.stderr}")

    lines = result.stdout.strip().split("\n")
    violations = []
    for line in lines:
        # radon format: "    M 10:4 method_name - C (12)"
        if " - " in line and "(" in line:
            parts = line.rsplit("(", 1)
            if len(parts) == 2:
                try:
                    cc = int(parts[1].rstrip(")"))
                    if cc > max_cc:
                        violations.append(line.strip())
                except ValueError:
                    pass

    if violations:
        return QualityResult(
            "Complexity",
            False,
            f"Methods exceeding CC {max_cc}:\n" + "\n".join(violations),
        )
    return QualityResult("Complexity", True, f"All methods CC <= {max_cc}")


def check_maintainability(path: Path, min_mi: int = 70) -> QualityResult:
    """Check maintainability index with radon."""
    result = run_cmd(["radon", "mi", "-s", str(path)])
    if result.returncode != 0:
        return QualityResult("Maintainability", False, f"radon failed: {result.stderr}")

    violations = []
    for line in result.stdout.strip().split("\n"):
        # radon mi format: "path/file.py - A (85.5)"
        if " - " in line and "(" in line:
            parts = line.rsplit("(", 1)
            if len(parts) == 2:
                try:
                    mi = float(parts[1].rstrip(")"))
                    if mi < min_mi:
                        violations.append(f"{line.strip()} (target: {min_mi}+)")
                except ValueError:
                    pass

    if violations:
        return QualityResult(
            "Maintainability",
            False,
            f"Files below MI {min_mi}:\n" + "\n".join(violations),
        )
    return QualityResult("Maintainability", True, f"All files MI >= {min_mi}")


def check_bandit(path: Path) -> QualityResult:
    """Run bandit security scan."""
    result = run_cmd(["bandit", "-r", "-ll", "-ii", str(path)])
    if result.returncode == 0:
        return QualityResult("Bandit", True, "No security issues found")
    return QualityResult("Bandit", False, result.stdout)


def check_coverage(path: Path, min_cov: int = 80) -> QualityResult:
    """Run pytest with coverage."""
    result = run_cmd(
        [
            "pytest",
            f"--cov={path}",
            "--cov-report=term-missing",
            f"--cov-fail-under={min_cov}",
            str(path),
        ]
    )
    if result.returncode == 0:
        return QualityResult("Coverage", True, f"Coverage >= {min_cov}%")
    return QualityResult("Coverage", False, f"Coverage < {min_cov}%\n{result.stdout}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run quality gates")
    parser.add_argument("path", type=Path, help="Path to check")
    parser.add_argument("--skip-coverage", action="store_true", help="Skip coverage")
    parser.add_argument("--min-coverage", type=int, default=80, help="Min coverage %")
    parser.add_argument("--max-complexity", type=int, default=10, help="Max CC")
    parser.add_argument("--min-maintainability", type=int, default=70, help="Min MI")
    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: {args.path} does not exist")
        return 1

    results: list[QualityResult] = [
        check_ruff(args.path),
        check_mypy(args.path),
        check_complexity(args.path, args.max_complexity),
        check_maintainability(args.path, args.min_maintainability),
        check_bandit(args.path),
    ]

    if not args.skip_coverage:
        results.append(check_coverage(args.path, args.min_coverage))

    print("\n" + "=" * 60)
    print("QUALITY GATE RESULTS")
    print("=" * 60)

    failed = []
    for r in results:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"\n[{status}] {r.name}")
        if not r.passed:
            print(f"  {r.message}")
            failed.append(r.name)

    print("\n" + "=" * 60)
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("ALL GATES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
