#!/usr/bin/env python3
"""
Test runner for engineering-verification Skill.

Runs all verification cases and reports results.

Usage:
    python test_runner.py
    python test_runner.py --verbose
    python test_runner.py --case reynolds_001
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
TESTS_DIR = SKILL_DIR / "tests" / "verification_cases"


class TestRunner:
    """Runs verification test cases."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []

    def run_verify(self, problem_file: Path, reported_value: Optional[float] = None) -> Dict[str, Any]:
        """Run verify.py on a problem file."""
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "verify.py"),
            "--problem-file", str(problem_file),
            "--output", "json"
        ]
        if reported_value is not None:
            cmd.extend(["--reported-value", str(reported_value)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr, "returncode": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": "Test timed out"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON output", "stdout": result.stdout}
        except Exception as e:
            return {"error": str(e)}

    def extract_reported_value(self, problem_file: Path) -> Optional[float]:
        """Extract reported value from problem markdown."""
        content = problem_file.read_text()
        # Look for reported result pattern
        import re
        patterns = [
            r'Reported Result\s*\n\s*Re\s*[=:]\s*([\d,\.]+)',
            r'Reported Result\s*\n\s*ΔP\s*[=:]\s*([\d,\.]+)\s*(kPa|Pa)?',
            r'Reported Result\s*\n\s*P₂\s*[=:]\s*([\d,\.]+)\s*(kPa|Pa)?',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                val_str = match.group(1).replace(',', '')
                try:
                    val = float(val_str)
                    # Convert kPa to Pa if needed
                    if len(match.groups()) > 1 and match.group(2) and 'kPa' in match.group(2):
                        val *= 1000
                    return val
                except ValueError:
                    pass
        return None

    def run_case(self, case_dir: Path, case_name: str) -> Dict[str, Any]:
        """Run a single test case."""
        problem_file = case_dir / "problem.md"
        expected_file = case_dir / "expected.md"

        if not problem_file.exists():
            return {"case": case_name, "status": "SKIP", "error": "No problem.md"}

        # Extract reported value from problem
        reported = self.extract_reported_value(problem_file)

        # Run verification
        result = self.run_verify(problem_file, reported)

        # Read expected verdict
        expected_verdict = "UNKNOWN"
        if expected_file.exists():
            content = expected_file.read_text()
            if "Expected Verdict" in content:
                for line in content.split('\n'):
                    if "Expected Verdict" in line:
                        expected_verdict = line.split(":")[-1].strip()
                        break

        # Determine test result
        actual_verdict = result.get("verdict", "ERROR")
        passed = actual_verdict == expected_verdict

        test_result = {
            "case": case_name,
            "problem": str(problem_file),
            "expected_verdict": expected_verdict,
            "actual_verdict": actual_verdict,
            "confidence": result.get("confidence", "N/A"),
            "passed": passed,
            "details": result
        }

        if self.verbose:
            print(f"  {case_name}: Expected={expected_verdict}, Actual={actual_verdict} {'✓' if passed else '✗'}")

        return test_result

    def run_all(self) -> Dict[str, Any]:
        """Run all test cases."""
        if not TESTS_DIR.exists():
            return {"error": f"Tests directory not found: {TESTS_DIR}"}

        # Find all test cases
        test_cases = []
        for domain_dir in TESTS_DIR.iterdir():
            if domain_dir.is_dir():
                for case_dir in domain_dir.iterdir():
                    if case_dir.is_dir() and (case_dir / "problem.md").exists():
                        case_name = f"{domain_dir.name}/{case_dir.name}"
                        test_cases.append((case_dir, case_name))

        print(f"Found {len(test_cases)} test cases")

        # Run each case
        for case_dir, case_name in test_cases:
            result = self.run_case(case_dir, case_name)
            self.results.append(result)

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("passed", False))
        failed = total - passed

        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0,
            "results": self.results
        }

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total:  {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Rate:   {summary['success_rate']:.1%}")
        print()

        if summary['failed'] > 0:
            print("FAILED CASES:")
            for r in summary['results']:
                if not r.get('passed', False):
                    print(f"  {r['case']}: Expected {r['expected_verdict']}, Got {r['actual_verdict']}")
            print()

        # Group by domain
        by_domain = {}
        for r in summary['results']:
            domain = r['case'].split('/')[0]
            if domain not in by_domain:
                by_domain[domain] = {"total": 0, "passed": 0}
            by_domain[domain]['total'] += 1
            if r.get('passed', False):
                by_domain[domain]['passed'] += 1

        print("BY DOMAIN:")
        for domain, stats in by_domain.items():
            print(f"  {domain}: {stats['passed']}/{stats['total']} ({stats['passed']/stats['total']:.1%})")


def main():
    parser = argparse.ArgumentParser(description="Test runner for engineering-verification Skill")
    parser.add_argument("--case", help="Run specific case (e.g., reynolds/reynolds_001)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output JSON summary")

    args = parser.parse_args()

    runner = TestRunner(verbose=args.verbose)

    if args.case:
        # Run single case
        case_dir = TESTS_DIR / args.case
        if not case_dir.exists():
            print(f"Case not found: {args.case}")
            sys.exit(1)
        result = runner.run_case(case_dir, args.case)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Case: {result['case']}")
            print(f"Expected: {result['expected_verdict']}")
            print(f"Actual:   {result['actual_verdict']}")
            print(f"Passed:   {result['passed']}")
        sys.exit(0 if result.get('passed', False) else 1)

    # Run all cases
    summary = runner.run_all()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        runner.print_summary(summary)

    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == "__main__":
    main()