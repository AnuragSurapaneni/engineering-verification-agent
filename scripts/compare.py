#!/usr/bin/env python3
"""
Result comparison tool for engineering verification.

Compares computed results against reported values with configurable tolerance.

Usage:
    python compare.py --computed 135000 --reported 135000 --tolerance 0.01
    python compare.py --computed '{"Reynolds_number": 135000}' --reported '{"Reynolds_number": 135000}' --key Reynolds_number
"""

import sys
import json
import argparse
from typing import Union, Dict, Any


def compare_values(computed: float, reported: float, tolerance: float = 0.01) -> Dict[str, Any]:
    """Compare two numerical values with relative tolerance."""
    if reported == 0:
        if computed == 0:
            rel_diff = 0.0
        else:
            rel_diff = float('inf')
    else:
        rel_diff = abs(computed - reported) / abs(reported)

    passed = rel_diff <= tolerance

    return {
        "passed": passed,
        "computed": computed,
        "reported": reported,
        "absolute_difference": abs(computed - reported),
        "relative_difference": rel_diff,
        "tolerance": tolerance,
        "difference_percent": rel_diff * 100
    }


def main():
    parser = argparse.ArgumentParser(description="Compare computed vs reported values")
    parser.add_argument("--computed", required=True, help="Computed value (number or JSON)")
    parser.add_argument("--reported", required=True, help="Reported value (number or JSON)")
    parser.add_argument("--tolerance", type=float, default=0.01, help="Relative tolerance (default: 0.01 = 1%)")
    parser.add_argument("--key", help="Key to extract from JSON objects")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")

    args = parser.parse_args()

    # Parse computed value
    try:
        computed_raw = json.loads(args.computed)
    except json.JSONDecodeError:
        try:
            computed_raw = float(args.computed)
        except ValueError:
            print(f"Error: --computed must be a number or valid JSON", file=sys.stderr)
            sys.exit(1)

    # Parse reported value
    try:
        reported_raw = json.loads(args.reported)
    except json.JSONDecodeError:
        try:
            reported_raw = float(args.reported)
        except ValueError:
            print(f"Error: --reported must be a number or valid JSON", file=sys.stderr)
            sys.exit(1)

    # Extract values if key provided
    if args.key:
        if not isinstance(computed_raw, dict) or args.key not in computed_raw:
            print(f"Error: Key '{args.key}' not found in computed JSON", file=sys.stderr)
            sys.exit(1)
        if not isinstance(reported_raw, dict) or args.key not in reported_raw:
            print(f"Error: Key '{args.key}' not found in reported JSON", file=sys.stderr)
            sys.exit(1)
        computed = computed_raw[args.key]
        reported = reported_raw[args.key]
    else:
        computed = computed_raw
        reported = reported_raw

    if not isinstance(computed, (int, float)) or not isinstance(reported, (int, float)):
        print("Error: Values to compare must be numbers", file=sys.stderr)
        sys.exit(1)

    result = compare_values(float(computed), float(reported), args.tolerance)

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()