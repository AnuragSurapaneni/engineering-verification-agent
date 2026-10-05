#!/usr/bin/env python3
"""
Numerical calculation engine for engineering verification.

Computes independent numerical results for standard engineering equations.

Usage:
    python calculate.py --problem reynolds_number --inputs '{"rho":1.177,"V":20,"D":0.1,"mu":1.85e-5}'
    python calculate.py --problem pressure_drop --inputs '{"f":0.02,"L":10,"D":0.05,"rho":997,"V":2}'
    python calculate.py --problem bernoulli --inputs '{"rho":997,"V1":3,"D1":0.1,"D2":0.05,"P1":200000}'
"""

import sys
import json
import argparse
import math
from typing import Dict, Any, Union


def calculate_reynolds(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Reynolds number: Re = rho * V * D / mu = V * D / nu"""
    # Support both rho+mu and nu
    if "nu" in inputs:
        Re = inputs["V"] * inputs["D"] / inputs["nu"]
    else:
        Re = inputs["rho"] * inputs["V"] * inputs["D"] / inputs["mu"]

    # Determine flow regime
    if Re < 2300:
        regime = "laminar"
    elif Re <= 4000:
        regime = "transitional"
    else:
        regime = "turbulent"

    return {
        "Reynolds_number": Re,
        "flow_regime": regime,
        "equation": "Re = rho*V*D/mu"
    }


def calculate_pressure_drop(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Darcy-Weisbach pressure drop: dP = f * (L/D) * (rho * V^2 / 2)"""
    f = inputs["f"]
    L = inputs["L"]
    D = inputs["D"]
    rho = inputs["rho"]
    V = inputs["V"]

    dP = f * (L / D) * (rho * V**2 / 2)

    return {
        "pressure_drop_Pa": dP,
        "pressure_drop_kPa": dP / 1000,
        "equation": "ΔP = f * (L/D) * (ρ * V² / 2)"
    }


def calculate_bernoulli(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Bernoulli: P2 = P1 + 0.5*rho*(V1^2 - V2^2) with continuity V2 = V1*(D1/D2)^2"""
    rho = inputs["rho"]
    V1 = inputs["V1"]
    D1 = inputs["D1"]
    D2 = inputs["D2"]
    P1 = inputs["P1"]

    # Continuity
    V2 = V1 * (D1 / D2)**2

    # Bernoulli (horizontal, no losses)
    P2 = P1 + 0.5 * rho * (V1**2 - V2**2)

    return {
        "velocity_2_m_s": V2,
        "pressure_2_Pa": P2,
        "pressure_2_kPa": P2 / 1000,
        "equation": "P2 = P1 + 0.5*rho*(V1^2 - V2^2), V2 = V1*(D1/D2)^2"
    }


PROBLEM_CALCULATORS = {
    "reynolds_number": calculate_reynolds,
    "pressure_drop": calculate_pressure_drop,
    "bernoulli": calculate_bernoulli,
}


def main():
    parser = argparse.ArgumentParser(description="Engineering calculation engine")
    parser.add_argument("--problem", required=True, choices=list(PROBLEM_CALCULATORS.keys()),
                        help="Problem type to calculate")
    parser.add_argument("--inputs", required=True, help="JSON string of input parameters")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")

    args = parser.parse_args()

    try:
        inputs = json.loads(args.inputs)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON inputs: {e}", file=sys.stderr)
        sys.exit(1)

    calculator = PROBLEM_CALCULATORS[args.problem]

    try:
        result = calculator(inputs)
    except KeyError as e:
        print(f"Error: Missing required input: {e}", file=sys.stderr)
        sys.exit(1)
    except ZeroDivisionError as e:
        print(f"Error: Division by zero in calculation: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Calculation failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()