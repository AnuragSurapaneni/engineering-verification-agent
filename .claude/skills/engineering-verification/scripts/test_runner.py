#!/usr/bin/env python3
"""Run the checked-in end-to-end verification cases."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
VERIFY_SCRIPT = Path(__file__).resolve().with_name("verify.py")
TESTS_DIR = REPOSITORY_ROOT / "tests" / "verification_cases"
SUPPORTED_DOMAINS = {"reynolds", "pressure_drop", "bernoulli"}
SUPPORTED_ROOT_CASES = {"mach_001"}
VERDICT_ALIASES = {
    "PASS": "VERIFIED",
    "FAIL": "NOT VERIFIED",
    "INSUFFICIENT_INFORMATION": "INSUFFICIENT INFORMATION",
}


class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []

    def run_verify(self, problem_file: Path) -> Dict[str, Any]:
        command = [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--problem-file", str(problem_file),
            "--output", "json",
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return {"error": "Verification timed out"}
        except OSError as exc:
            return {"error": f"Could not start verifier: {exc}"}
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "error": "Verifier did not return valid JSON",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        if result.returncode not in (0, 1, 2):
            payload["runner_error"] = result.stderr.strip() or f"Unexpected verifier exit code {result.returncode}"
        return payload

    @staticmethod
    def expected_verdict(expected_file: Path) -> str:
        if not expected_file.exists():
            return "UNKNOWN"
        lines = expected_file.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if "Expected Verdict" in line:
                for candidate in lines[index + 1:]:
                    value = candidate.strip()
                    if value:
                        return VERDICT_ALIASES.get(value, value)
        return "UNKNOWN"

    def run_case(self, case_dir: Path, case_name: str) -> Dict[str, Any]:
        problem_file = case_dir / "problem.md"
        expected_file = case_dir / "expected.md"
        if not problem_file.exists():
            return {"case": case_name, "passed": False, "error": "No problem.md"}

        result = self.run_verify(problem_file)
        expected = self.expected_verdict(expected_file)
        actual = result.get("verdict", "ERROR")
        passed = actual == expected
        item = {
            "case": case_name,
            "problem": str(problem_file),
            "expected_verdict": expected,
            "actual_verdict": actual,
            "confidence": result.get("confidence", "N/A"),
            "passed": passed,
            "details": result,
        }
        if self.verbose:
            mark = "PASS" if passed else "FAIL"
            print(f"{case_name}: expected {expected}, got {actual} ({mark})")
        return item

    def discover_cases(self) -> List[Tuple[Path, str]]:
        cases: List[Tuple[Path, str]] = []
        if not TESTS_DIR.is_dir():
            return cases
        for domain in sorted(TESTS_DIR.iterdir()):
            if not domain.is_dir():
                continue
            if domain.name in SUPPORTED_DOMAINS:
                for case_dir in sorted(domain.iterdir()):
                    if case_dir.is_dir() and (case_dir / "problem.md").is_file():
                        cases.append((case_dir, f"{domain.name}/{case_dir.name}"))
            elif domain.name in SUPPORTED_ROOT_CASES and (domain / "problem.md").is_file():
                cases.append((domain, domain.name))
        return cases

    def run_all(self) -> Dict[str, Any]:
        if not TESTS_DIR.is_dir():
            return {"error": f"Verification cases directory not found: {TESTS_DIR}", "total": 0, "passed": 0, "failed": 0, "results": []}
        self.results = [self.run_case(case_dir, name) for case_dir, name in self.discover_cases()]
        total = len(self.results)
        passed = sum(1 for item in self.results if item.get("passed"))
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": passed / total if total else 0.0,
            "results": self.results,
        }

    @staticmethod
    def print_summary(summary: Dict[str, Any]) -> None:
        print("TEST SUMMARY")
        print(f"Total:  {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Rate:   {summary['success_rate']:.1%}")
        for item in summary.get("results", []):
            if not item.get("passed"):
                print(f"  {item['case']}: expected {item.get('expected_verdict')}, got {item.get('actual_verdict', 'ERROR')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run checked-in verification cases")
    parser.add_argument("--case", help="Case path, for example reynolds/reynolds_001 or mach_001")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()
    runner = TestRunner(verbose=args.verbose)

    if args.case:
        case_dir = (TESTS_DIR / args.case).resolve()
        try:
            case_dir.relative_to(TESTS_DIR.resolve())
        except ValueError:
            parser.error("--case must refer to a case under tests/verification_cases")
        relative_parts = case_dir.relative_to(TESTS_DIR.resolve()).parts
        supported = bool(relative_parts) and (
            relative_parts[0] in SUPPORTED_DOMAINS
            or (len(relative_parts) == 1 and relative_parts[0] in SUPPORTED_ROOT_CASES)
        )
        if not supported:
            parser.error("that case is calculator-only and has no end-to-end verification workflow")
        result = runner.run_case(case_dir, args.case)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Case:    {result['case']}")
            print(f"Expected: {result.get('expected_verdict', 'UNKNOWN')}")
            print(f"Actual:   {result.get('actual_verdict', 'ERROR')}")
            print(f"Passed:   {result.get('passed', False)}")
        sys.exit(0 if result.get("passed") else 1)

    summary = runner.run_all()
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        runner.print_summary(summary)
    sys.exit(0 if summary.get("failed", 1) == 0 and summary.get("total", 0) > 0 else 1)


if __name__ == "__main__":
    main()
