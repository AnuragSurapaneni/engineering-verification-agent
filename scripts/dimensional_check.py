#!/usr/bin/env python3
"""Check equation dimensions using SI base dimensions."""

import argparse
import json
import re
import sys
from typing import Dict, Optional, Tuple

from units import get_dimensions

Dimensions = Dict[str, float]


VARIABLE_DIMENSIONS: Dict[str, Dimensions] = {
    "rho": {"M": 1, "L": -3},
    "mu": {"M": 1, "L": -1, "T": -1},
    "nu": {"L": 2, "T": -1},
    "V": {"L": 1, "T": -1},
    "V1": {"L": 1, "T": -1},
    "V2": {"L": 1, "T": -1},
    "D": {"L": 1},
    "D1": {"L": 1},
    "D2": {"L": 1},
    "L": {"L": 1},
    "x": {"L": 1},
    "r": {"L": 1},
    "f": {},
    "Re": {},
    "Re_x": {},
    "M": {},
    "gamma": {},
    "pi": {},
    "theta": {},
    "Theta": {"Theta": 1},
    "P": {"M": 1, "L": -1, "T": -2},
    "P1": {"M": 1, "L": -1, "T": -2},
    "P2": {"M": 1, "L": -1, "T": -2},
    "dP": {"M": 1, "L": -1, "T": -2},
    "deltaP": {"M": 1, "L": -1, "T": -2},
    "z": {"L": 1},
    "z1": {"L": 1},
    "z2": {"L": 1},
    "g": {"L": 1, "T": -2},
    "h": {"L": 1},
    "T": {"Theta": 1},
    "T0": {"Theta": 1},
    "a": {"L": 1, "T": -1},
    "R": {"L": 2, "T": -2, "Theta": -1},
    "Cp": {"L": 2, "T": -2, "Theta": -1},
    "cp": {"L": 2, "T": -2, "Theta": -1},
    "k": {"M": 1, "L": 1, "T": -3, "Theta": -1},
    "sigma": {"M": 1, "T": -2},
    "A": {"L": 2},
    "A_c": {"L": 2},
    "A1": {"L": 2},
    "A2": {"L": 2},
    "A_star": {"L": 2},
    "P_wetted": {"L": 1},
    "Q": {"L": 3, "T": -1},
    "epsilon": {"L": 1},
    "epsilon_turb": {"L": 2, "T": -3},
    "k_turb": {"L": 2, "T": -2},
    "mu_t": {"M": 1, "L": -1, "T": -1},
    "V_theta": {"L": 1, "T": -1},
    "U": {"L": 1, "T": -1},
    "omega": {"T": -1},
    "Gamma": {"L": 2, "T": -1},
    "delta": {"L": 1},
    "y_plus": {},
    "C_f": {},
    "C_L": {},
    "C_D": {},
    "CD": {},
    "e": {},
    "alpha": {},
    "AR": {},
    "b": {"L": 1},
    "S": {"L": 2},
    "FD": {"M": 1, "L": 1, "T": -2},
    "FL": {"M": 1, "L": 1, "T": -2},
    "F_D": {"M": 1, "L": 1, "T": -2},
    "F_L": {"M": 1, "L": 1, "T": -2},
    "D_AB": {"L": 2, "T": -1},
}

# Only aliases with the same physical dimensions belong here. Variables whose
# meanings differ by dimensions are declared explicitly above.
FALLBACK_VARIABLES = {
    "CL_max": "C_L",
    "C_D_0": "C_D",
}

GREEK_REPLACEMENTS = {
    "ρ": "rho", "μ": "mu", "ν": "nu", "γ": "gamma", "σ": "sigma",
    "δ": "delta", "ΔP": "deltaP", "Δp": "deltaP", "θ": "theta",
    "Θ": "Theta", "π": "pi",
}
SUPERSCRIPTS = str.maketrans({"⁰": "0", "¹": "1", "²": "2", "³": "3",
                              "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7",
                              "⁸": "8", "⁹": "9", "⁻": "-", "⁺": "+"})


class DimensionalAnalysisError(ValueError):
    """Raised for malformed expressions or unknown variables."""


def _clean(dims: Dimensions) -> Dimensions:
    return {key: value for key, value in dims.items() if abs(value) > 1e-12}


def _combine(left: Dimensions, right: Dimensions, sign: float) -> Dimensions:
    result = dict(left)
    for base, exponent in right.items():
        result[base] = result.get(base, 0) + sign * exponent
    return _clean(result)


def _scale(dims: Dimensions, factor: float) -> Dimensions:
    return _clean({base: exponent * factor for base, exponent in dims.items()})


class _ExpressionParser:
    def __init__(self, expression: str):
        self.expression = self._normalize(expression)
        self.tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|(?:\d+(?:\.\d*)?|\.\d+)|\*\*|[()+\-*/^,]", self.expression)
        residue = re.sub(r"\s+", "", re.sub(r"[A-Za-z_][A-Za-z0-9_]*|(?:\d+(?:\.\d*)?|\.\d+)|\*\*|[()+\-*/^,]", "", self.expression))
        if residue:
            raise DimensionalAnalysisError(f"Unsupported token(s): {residue}")
        self.position = 0

    @staticmethod
    def _normalize(expression: str) -> str:
        result = expression.translate(SUPERSCRIPTS)
        # Replace longer Greek symbols first (for example ΔP before P).
        for symbol in sorted(GREEK_REPLACEMENTS, key=len, reverse=True):
            result = result.replace(symbol, GREEK_REPLACEMENTS[symbol])
        result = result.replace("≈", "=").replace("·", "*")
        return result

    def peek(self) -> Optional[str]:
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise DimensionalAnalysisError("Unexpected end of expression")
        self.position += 1
        return token

    def parse(self) -> Tuple[Dimensions, Optional[float]]:
        dimensions, value = self.parse_sum()
        if self.peek() is not None:
            raise DimensionalAnalysisError(f"Unexpected token '{self.peek()}'")
        return dimensions, value

    def parse_sum(self) -> Tuple[Dimensions, Optional[float]]:
        left_dims, left_value = self.parse_product()
        while self.peek() in ("+", "-"):
            op = self.take()
            right_dims, right_value = self.parse_product()
            if left_dims != right_dims:
                raise DimensionalAnalysisError("Addition/subtraction requires matching dimensions")
            if left_value is None or right_value is None:
                left_value = None
            else:
                left_value = left_value + right_value if op == "+" else left_value - right_value
        return left_dims, left_value

    def parse_product(self) -> Tuple[Dimensions, Optional[float]]:
        left_dims, left_value = self.parse_power()
        while self.peek() in ("*", "/"):
            op = self.take()
            right_dims, right_value = self.parse_power()
            sign = 1 if op == "*" else -1
            left_dims = _combine(left_dims, right_dims, sign)
            if left_value is None or right_value is None or (op == "/" and right_value == 0):
                left_value = None
            else:
                left_value = left_value * right_value if op == "*" else left_value / right_value
        return left_dims, left_value

    def parse_power(self) -> Tuple[Dimensions, Optional[float]]:
        dimensions, value = self.parse_unary()
        if self.peek() in ("^", "**"):
            self.take()
            exponent_dims, exponent = self.parse_unary()
            if exponent_dims or exponent is None:
                raise DimensionalAnalysisError("Exponent must be a numeric dimensionless value")
            dimensions = _scale(dimensions, exponent)
            value = value ** exponent if value is not None else None
        return dimensions, value

    def parse_unary(self) -> Tuple[Dimensions, Optional[float]]:
        if self.peek() in ("+", "-"):
            sign = -1 if self.take() == "-" else 1
            dimensions, value = self.parse_unary()
            return dimensions, value * sign if value is not None else None
        return self.parse_primary()

    def parse_primary(self) -> Tuple[Dimensions, Optional[float]]:
        token = self.take()
        if token == "(":
            dimensions, value = self.parse_sum()
            if self.take() != ")":
                raise DimensionalAnalysisError("Expected closing parenthesis")
            return dimensions, value
        if re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", token):
            return {}, float(token)
        if token == "," or token in (")", "*", "/", "^", "**", "+", "-"):
            raise DimensionalAnalysisError(f"Unexpected token '{token}'")
        if self.peek() == "(":
            self.take()
            dimensions, _ = self.parse_sum()
            if self.take() != ")":
                raise DimensionalAnalysisError("Expected closing parenthesis")
            if token == "sqrt":
                return _scale(dimensions, 0.5), None
            if token.lower() in ("ln", "log", "log10", "exp", "sin", "cos", "tan"):
                if dimensions:
                    raise DimensionalAnalysisError(f"{token} requires a dimensionless argument")
                return {}, None
            raise DimensionalAnalysisError(f"Unsupported function '{token}'")
        variable = token
        dimensions = VARIABLE_DIMENSIONS.get(variable)
        if dimensions is None:
            fallback = FALLBACK_VARIABLES.get(variable)
            dimensions = VARIABLE_DIMENSIONS.get(fallback) if fallback else None
        if dimensions is None:
            raise DimensionalAnalysisError(f"Unknown variable '{variable}'")
        return dict(dimensions), None


def parse_equation(equation: str) -> Dimensions:
    """Return dimensions of the right-hand side and check both equation sides."""
    normalized = _ExpressionParser._normalize(equation)
    if "=" in normalized:
        left_text, right_text = normalized.split("=", 1)
        left_dims, _ = _ExpressionParser(left_text).parse()
        right_dims, _ = _ExpressionParser(right_text).parse()
        if left_dims != right_dims:
            raise DimensionalAnalysisError("Left and right sides have different dimensions")
        return right_dims
    return _ExpressionParser(normalized).parse()[0]


def format_dimensions(dims: Dimensions) -> str:
    if not dims:
        return "dimensionless"
    labels = {"M": "M", "L": "L", "T": "T", "Theta": "Θ", "N": "N", "I": "I", "J": "J"}
    order = ["M", "L", "T", "Theta", "N", "I", "J"]
    parts = []
    for base in order:
        if base in dims:
            exponent = dims[base]
            shown = int(exponent) if float(exponent).is_integer() else exponent
            parts.append(labels[base] if exponent == 1 else f"{labels[base]}^{shown}")
    return " ".join(parts)


def expected_dimensions(target: str) -> Dimensions:
    if target.lower() in ("dimensionless", "1", ""):
        return {}
    variable = target.strip()
    if variable in VARIABLE_DIMENSIONS:
        return dict(VARIABLE_DIMENSIONS[variable])
    fallback = FALLBACK_VARIABLES.get(variable)
    if fallback:
        return dict(VARIABLE_DIMENSIONS[fallback])
    common_units = {
        "Pa": {"M": 1, "L": -1, "T": -2},
        "N": {"M": 1, "L": 1, "T": -2},
        "J": {"M": 1, "L": 2, "T": -2},
        "W": {"M": 1, "L": 2, "T": -3},
    }
    if variable in common_units:
        return dict(common_units[variable])
    unit_aliases = {"Pa": "pascal", "N": "newton", "J": "joule", "W": "watt"}
    unit = unit_aliases.get(variable, variable)
    try:
        dims = get_dimensions(unit)
    except Exception as exc:
        raise DimensionalAnalysisError(f"Unknown expected dimension or unit '{target}'") from exc
    conversion = {
        "[mass]": "M", "[length]": "L", "[time]": "T", "[temperature]": "Theta",
        "[amount]": "N", "[current]": "I", "[luminosity]": "J", "[luminous intensity]": "J",
    }
    return {conversion.get(key, key): value for key, value in dims.items() if value}


def check_equation(equation: str, expected: str) -> Dict[str, object]:
    try:
        computed = parse_equation(equation)
        target = expected_dimensions(expected)
        match = computed == target
        error = None
    except DimensionalAnalysisError as exc:
        computed = {}
        target = {}
        match = False
        error = str(exc)
    return {
        "equation": equation,
        "expected": expected,
        "expected_dimensions": format_dimensions(target),
        "computed_dimensions": format_dimensions(computed),
        "computed_raw": computed,
        "expected_raw": target,
        "match": match,
        "error": error,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check dimensional consistency of an equation")
    parser.add_argument("--equation", required=True, help="Equation to check")
    parser.add_argument("--expected", required=True, help="Expected unit or dimension (for example Pa)")
    parser.add_argument("--verbose", action="store_true", help="Print structured JSON")
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
        if result["error"]:
            print(f"  Error: {result['error']}")
    sys.exit(0 if result["match"] else 1)


if __name__ == "__main__":
    main()
