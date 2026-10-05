#!/usr/bin/env python3
"""
Dimensional analysis checker for engineering equations.

Verifies that equations are dimensionally consistent by analyzing
the dimensions of each variable in the equation.

Usage:
    python dimensional_check.py --equation "rho*V*D/mu" --expected dimensionless
    python dimensional_check.py --equation "f*L/D*rho*V^2/2" --expected "Pa"
"""

import sys
import json
import argparse
import re
from typing import Dict, List, Tuple, Optional, Any
from units import get_dimensions, check_dimensionless


# Standard variable dimensions (SI base: L, M, T, Θ, N, I, J)
# L=length, M=mass, T=time, Θ=temperature, N=amount, I=current, J=luminous
VARIABLE_DIMENSIONS = {
    # Fluid properties
    "rho": {"M": 1, "L": -3},           # density kg/m³
    "mu": {"M": 1, "L": -1, "T": -1},   # dynamic viscosity Pa·s = kg/(m·s)
    "nu": {"L": 2, "T": -1},            # kinematic viscosity m²/s
    "V": {"L": 1, "T": -1},             # velocity m/s
    "D": {"L": 1},                      # diameter m
    "L": {"L": 1},                      # length m
    "f": {},                            # friction factor (dimensionless)
    "Re": {},                           # Reynolds number (dimensionless)
    # Pressure/Force
    "P": {"M": 1, "L": -1, "T": -2},    # pressure Pa = N/m² = kg/(m·s²)
    "dP": {"M": 1, "L": -1, "T": -2},   # pressure drop
    "deltaP": {"M": 1, "L": -1, "T": -2},
    # Energy/Head
    "z": {"L": 1},                      # elevation m
    "g": {"L": 1, "T": -2},             # gravity m/s²
    "h": {"L": 1},                      # head m
    # Thermodynamics
    "T": {"Θ": 1},                      # temperature K
    "Cp": {"L": 2, "T": -2, "Θ": -1},   # specific heat J/(kg·K)
    "k": {"M": 1, "L": 1, "T": -3, "Θ": -1},  # thermal conductivity W/(m·K)
}


def parse_equation(equation: str) -> Dict[str, int]:
    """
    Parse equation and return combined dimensions.
    Handles *, /, ^ operators with proper precedence.
    Returns dict of base dimension -> exponent.
    """
    # Remove spaces
    eq = equation.replace(" ", "")

    # Split by = if present (take RHS)
    if "=" in eq:
        eq = eq.split("=")[1]

    # Tokenize: variables, numbers, operators, parentheses
    # Pattern matches: variable names, numbers, ^, *, /, (, )
    tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|\^|\*|/|\(|\)', eq)

    # Convert to postfix notation (Shunting Yard algorithm) for proper precedence
    # Precedence: ^ (highest, right-associative), * and / (left-associative)
    output = []
    operators = []

    precedence = {"^": 3, "*": 2, "/": 2}
    right_assoc = {"^"}

    def apply_operator(op: str, stack: List[Dict[str, int]]) -> Dict[str, int]:
        """Apply operator to top items on stack."""
        if op == "^":
            # Exponentiation: pop base and exponent
            if len(stack) < 2:
                return {}
            exp = stack.pop()
            base = stack.pop()
            # Exponent should be a number (dimensionless)
            if not exp:
                # dimensionless exponent - multiply base dimensions by exponent value
                return base
            # For dimensional analysis, we assume exponent is dimensionless number
            # We can't evaluate it here, so we just return base (exponent handled elsewhere)
            return base
        elif op in ("*", "/"):
            if len(stack) < 2:
                return {}
            right = stack.pop()
            left = stack.pop()
            if op == "*":
                return multiply_dims(left, right)
            else:
                return divide_dims(left, right)
        return {}

    def multiply_dims(a: Dict[str, int], b: Dict[str, int]) -> Dict[str, int]:
        result = a.copy()
        for base, exp in b.items():
            result[base] = result.get(base, 0) + exp
        return {k: v for k, v in result.items() if v != 0}

    def divide_dims(a: Dict[str, int], b: Dict[str, int]) -> Dict[str, int]:
        result = a.copy()
        for base, exp in b.items():
            result[base] = result.get(base, 0) - exp
        return {k: v for k, v in result.items() if v != 0}

    # For dimensional analysis, we can simplify by directly parsing
    # Since we only care about dimensions, not values, we can track
    # numerator and denominator separately with exponent handling

    # Simple approach: recursively parse with proper handling of ^
    # We'll use a recursive descent parser

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def consume(self):
            tok = self.peek()
            self.pos += 1
            return tok

        def parse(self) -> Dict[str, int]:
            return self.parse_expression()

        def parse_expression(self) -> Dict[str, int]:
            """Parse addition/subtraction (not used in dimensional analysis, but for completeness)"""
            return self.parse_term()

        def parse_term(self) -> Dict[str, int]:
            """Parse multiplication/division"""
            left = self.parse_factor()
            while self.peek() in ("*", "/"):
                op = self.consume()
                right = self.parse_factor()
                if op == "*":
                    left = multiply_dims(left, right)
                else:
                    left = divide_dims(left, right)
            return left

        def parse_factor(self) -> Dict[str, int]:
            """Parse exponentiation (right-associative)"""
            left = self.parse_primary()
            if self.peek() == "^":
                self.consume()  # consume ^
                # For exponentiation, we need to parse the exponent as a primary to get its value
                # Save position to check if exponent is a number
                exp_start = self.pos
                right = self.parse_primary()
                # Check if the exponent was a number
                if exp_start < len(self.tokens) and re.match(r'\d+\.?\d*', self.tokens[exp_start]):
                    # Exponent is a number - multiply dimensions by this value
                    try:
                        exp_val = float(self.tokens[exp_start])
                        # Multiply all dimensions by exponent value
                        left = {k: int(v * exp_val) for k, v in left.items()}
                    except (ValueError, TypeError):
                        pass  # If we can't parse, just use base dimensions
                return left
            return left

        def parse_primary(self) -> Dict[str, int]:
            """Parse variables, numbers, parentheses"""
            tok = self.peek()
            if tok is None:
                return {}
            if tok == "(":
                self.consume()
                result = self.parse_expression()
                if self.peek() == ")":
                    self.consume()
                return result
            elif tok == ")":
                return {}
            elif re.match(r'\d+\.?\d*', tok):
                self.consume()
                return {}  # numbers are dimensionless
            else:
                # Variable
                self.consume()
                var = tok
                dims = VARIABLE_DIMENSIONS.get(var)
                if dims is None:
                    try:
                        dims = get_dimensions(var)
                    except Exception:
                        dims = {}
                        print(f"Warning: Unknown variable '{var}', treating as dimensionless", file=sys.stderr)
                return dims.copy() if dims else {}

    parser = Parser(tokens)
    return parser.parse()


def format_dimensions(dims: Dict[str, int]) -> str:
    """Format dimensions as a readable string."""
    if not dims:
        return "dimensionless"
    parts = []
    for base in ["M", "L", "T", "Θ", "N", "I", "J"]:
        if base in dims:
            exp = dims[base]
            if exp == 1:
                parts.append(base)
            else:
                parts.append(f"{base}^{exp}")
    return " ".join(parts)


def expected_dimensions(target: str) -> Dict[str, int]:
    """Get expected dimensions for a target quantity."""
    if target.lower() in ("dimensionless", "1", ""):
        return {}
    if target in VARIABLE_DIMENSIONS:
        return VARIABLE_DIMENSIONS[target]
    # Try to get from units module, but convert pint format to our format
    try:
        dims = get_dimensions(target)
        # Convert pint dimension names to our format
        conversion = {
            "[mass]": "M",
            "[length]": "L",
            "[time]": "T",
            "[temperature]": "Θ",
            "[amount]": "N",
            "[current]": "I",
            "[luminous]": "J",
        }
        converted = {}
        for k, v in dims.items():
            converted[conversion.get(k, k)] = v
        return converted
    except Exception:
        return {}


def check_equation(equation: str, expected: str) -> Dict[str, Any]:
    """Check dimensional consistency of an equation."""
    result_dims = parse_equation(equation)
    expected_dims = expected_dimensions(expected)

    match = result_dims == expected_dims

    return {
        "equation": equation,
        "expected": expected,
        "expected_dimensions": format_dimensions(expected_dims),
        "computed_dimensions": format_dimensions(result_dims),
        "computed_raw": result_dims,
        "expected_raw": expected_dims,
        "match": match,
    }


def main():
    parser = argparse.ArgumentParser(description="Dimensional analysis checker")
    parser.add_argument("--equation", required=True, help="Equation to check (e.g., 'rho*V*D/mu')")
    parser.add_argument("--expected", required=True, help="Expected result (e.g., 'dimensionless', 'Pa', 'Re')")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    result = check_equation(args.equation, args.expected)

    if args.verbose:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["match"] else "FAIL"
        print(f"DIMENSIONAL CHECK: {status}")
        print(f"  Equation: {result['equation']}")
        print(f"  Expected: {result['expected_dimensions']}")
        print(f"  Computed: {result['computed_dimensions']}")
        if not result["match"]:
            print(f"  Computed raw: {result['computed_raw']}")
            print(f"  Expected raw: {result['expected_raw']}")
        sys.exit(0 if result["match"] else 1)


if __name__ == "__main__":
    main()