#!/usr/bin/env python3
"""Score equation-audit verdicts and check benchmark dimensional expectations."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
CASES_FILE = Path(__file__).with_name("benchmark_cases.json")
sys.path.insert(0, str(ROOT / "scripts"))

from dimensional_check import check_equation  # noqa: E402


VERDICTS = ("Correct", "Incorrect", "Uncertain")
DIMENSION_STATUSES = ("pass", "fail", "unsupported")


def load_cases() -> List[Dict[str, Any]]:
    payload = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"No benchmark cases found in {CASES_FILE}")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)) or any(not case_id for case_id in ids):
        raise ValueError("Benchmark case IDs must be present and unique")
    for case in cases:
        if case.get("verdict") not in VERDICTS:
            raise ValueError(f"Invalid expected verdict for {case.get('id')}")
        dimension = case.get("dimension")
        if not isinstance(dimension, dict) or dimension.get("status") not in DIMENSION_STATUSES:
            raise ValueError(f"Invalid dimension expectation for {case.get('id')}")
    return cases


def check_dimensions(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    for case in cases:
        spec = case["dimension"]
        expected_status = spec["status"]
        result: Optional[Dict[str, Any]] = None
        if expected_status == "unsupported":
            actual_status = "unsupported"
        else:
            result = check_equation(
                spec["equation"], spec["expected"], case["domain"]
            )
            if result["match"]:
                actual_status = "pass"
            elif result["error"] and any(
                marker in result["error"]
                for marker in (
                    "Unknown variable",
                    "Unsupported token",
                    "Unsupported function",
                    "Unexpected token",
                )
            ):
                actual_status = "unsupported"
            else:
                actual_status = "fail"
        rows.append({
            "id": case["id"],
            "expected": expected_status,
            "actual": actual_status,
            "passed": expected_status == actual_status,
            "checker_error": result["error"] if result else None,
        })
    passed = sum(row["passed"] for row in rows)
    return {
        "total": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
        "unsupported": sum(row["expected"] == "unsupported" for row in rows),
        "success_rate": passed / len(rows) if rows else 0.0,
        "results": rows,
    }


def load_predictions(path: Path) -> Dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("results") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("Results JSON must be an array or an object with a 'results' array")
    predictions: Dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("Each result must have a string 'id' and a verdict")
        case_id = row["id"]
        if case_id in predictions:
            raise ValueError(f"Duplicate result ID: {case_id}")
        verdict = row.get("verdict")
        if verdict not in VERDICTS:
            raise ValueError(f"Invalid verdict for {case_id}: {verdict}")
        predictions[case_id] = verdict
    return predictions


def score_predictions(
    cases: List[Dict[str, Any]], predictions: Dict[str, str]
) -> Dict[str, Any]:
    expected = {case["id"]: case["verdict"] for case in cases}
    unknown = sorted(set(predictions) - set(expected))
    missing = sorted(set(expected) - set(predictions))
    confusion: Dict[str, Counter] = {label: Counter() for label in VERDICTS}
    per_domain: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0})
    rows = []
    for case in cases:
        case_id = case["id"]
        actual = predictions.get(case_id)
        target = case["verdict"]
        if actual is not None:
            confusion[target][actual] += 1
        passed = actual == target
        counts = per_domain[case["domain"]]
        counts["total"] += 1
        counts["passed"] += int(passed)
        rows.append({
            "id": case_id,
            "domain": case["domain"],
            "expected": target,
            "actual": actual,
            "passed": passed,
        })
    for counts in per_domain.values():
        counts["success_rate"] = counts["passed"] / counts["total"] if counts["total"] else 0.0
    passed = sum(row["passed"] for row in rows)
    return {
        "total": len(cases),
        "passed": passed,
        "failed": len(cases) - passed,
        "success_rate": passed / len(cases) if cases else 0.0,
        "missing_ids": missing,
        "unknown_ids": unknown,
        "per_domain": dict(sorted(per_domain.items())),
        "confusion_matrix": {
            target: {pred: confusion[target][pred] for pred in VERDICTS}
            for target in VERDICTS
        },
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, help="JSON verdicts to score against the reference key")
    parser.add_argument("--check-dimensions", action="store_true", help="Run benchmark dimensional checks")
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON")
    args = parser.parse_args()

    try:
        cases = load_cases()
        output: Dict[str, Any] = {
            "benchmark": str(CASES_FILE.relative_to(ROOT)),
            "case_count": len(cases),
        }
        if args.check_dimensions or not args.results:
            output["dimension_checks"] = check_dimensions(cases)
        if args.results:
            output["verdict_score"] = score_predictions(cases, load_predictions(args.results))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Benchmark error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"Equation audit benchmark: {output['case_count']} cases")
        if "dimension_checks" in output:
            result = output["dimension_checks"]
            print(f"Dimensions: {result['passed']}/{result['total']} expectations matched; {result['unsupported']} intentionally unsupported")
            for row in result["results"]:
                if not row["passed"]:
                    print(f"  {row['id']}: expected {row['expected']}, got {row['actual']} ({row['checker_error']})")
        if "verdict_score" in output:
            result = output["verdict_score"]
            print(f"Verdicts: {result['passed']}/{result['total']} ({result['success_rate']:.1%})")
            for domain, counts in result["per_domain"].items():
                print(f"  {domain}: {counts['passed']}/{counts['total']} ({counts['success_rate']:.1%})")
            if result["missing_ids"]:
                print(f"  missing IDs: {', '.join(result['missing_ids'])}")
            if result["unknown_ids"]:
                print(f"  unknown IDs: {', '.join(result['unknown_ids'])}")
            for row in result["results"]:
                if not row["passed"]:
                    print(f"  {row['id']}: expected {row['expected']}, got {row['actual']}")

    checks_ok = output.get("dimension_checks", {}).get("failed", 0) == 0
    verdicts = output.get("verdict_score")
    verdicts_ok = verdicts is None or (
        verdicts["failed"] == 0 and not verdicts["missing_ids"] and not verdicts["unknown_ids"]
    )
    return 0 if checks_ok and verdicts_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
