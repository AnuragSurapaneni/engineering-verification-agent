#!/usr/bin/env python3
"""
Units abstraction layer for engineering verification.

Provides a thin wrapper around Pint (or alternative unit libraries)
to enable unit conversion, dimensional analysis, and quantity handling.

Usage:
    from units import convert, get_dimensions, Quantity
    convert(72, "km/h", "m/s")  # Returns 20.0
    get_dimensions("m/s")  # Returns {"L": 1, "T": -1}
"""

import sys
import json
from typing import Dict, Any, Optional, Union

try:
    import pint
    HAS_PINT = True
except ImportError:
    HAS_PINT = False
    print("Warning: Pint not installed. Install with: pip install pint", file=sys.stderr)


class UnitRegistry:
    """Wrapper around Pint's UnitRegistry for abstraction."""

    def __init__(self):
        if HAS_PINT:
            self._ureg = pint.UnitRegistry()
            self._ureg.default_format = "~P"
        else:
            self._ureg = None

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert a value from one unit to another."""
        if not self._ureg:
            raise RuntimeError("Pint not available")
        try:
            q = self._ureg.Quantity(value, from_unit)
            return float(q.to(to_unit).magnitude)
        except Exception as e:
            raise ValueError(f"Conversion failed: {value} {from_unit} -> {to_unit}: {e}")

    def get_dimensions(self, unit: str) -> Dict[str, int]:
        """Get the dimensional formula for a unit as a dict."""
        if not self._ureg:
            raise RuntimeError("Pint not available")
        try:
            q = self._ureg.Quantity(1, unit)
            dims = q.dimensionality
            return {str(k): int(v) for k, v in dims.items()}
        except Exception as e:
            raise ValueError(f"Failed to get dimensions for {unit}: {e}")

    def check_dimensionless(self, unit: str) -> bool:
        """Check if a unit is dimensionless."""
        dims = self.get_dimensions(unit)
        return all(v == 0 for v in dims.values())

    def to_si(self, value: float, unit: str) -> tuple[float, str]:
        """Convert to base SI units."""
        if not self._ureg:
            raise RuntimeError("Pint not available")
        try:
            q = self._ureg.Quantity(value, unit)
            si = q.to_base_units()
            return float(si.magnitude), str(si.units)
        except Exception as e:
            raise ValueError(f"SI conversion failed: {e}")

    def quantity(self, value: float, unit: str) -> Any:
        """Create a quantity object."""
        if not self._ureg:
            raise RuntimeError("Pint not available")
        return self._ureg.Quantity(value, unit)


# Global registry instance
_registry = UnitRegistry()


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a value from one unit to another."""
    return _registry.convert(value, from_unit, to_unit)


def get_dimensions(unit: str) -> Dict[str, int]:
    """Get dimensional formula for a unit."""
    return _registry.get_dimensions(unit)


def check_dimensionless(unit: str) -> bool:
    """Check if a unit is dimensionless."""
    return _registry.check_dimensionless(unit)


def to_si(value: float, unit: str) -> tuple[float, str]:
    """Convert to base SI units."""
    return _registry.to_si(value, unit)


def Quantity(value: float, unit: str):
    """Create a quantity object."""
    return _registry.quantity(value, unit)


# CLI interface
def main():
    if len(sys.argv) < 2:
        print("Usage: units.py <command> [args...]")
        print("Commands:")
        print("  convert --value VAL --from UNIT --to UNIT")
        print("  dimensions --unit UNIT")
        print("  si --value VAL --unit UNIT")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "convert":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--value", type=float, required=True)
        parser.add_argument("--from", dest="from_unit", required=True)
        parser.add_argument("--to", dest="to_unit", required=True)
        args = parser.parse_args(sys.argv[2:])
        result = convert(args.value, args.from_unit, args.to_unit)
        print(result)

    elif cmd == "dimensions":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--unit", required=True)
        args = parser.parse_args(sys.argv[2:])
        dims = get_dimensions(args.unit)
        print(json.dumps(dims))

    elif cmd == "si":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--value", type=float, required=True)
        parser.add_argument("--unit", required=True)
        args = parser.parse_args(sys.argv[2:])
        val, unit = to_si(args.value, args.unit)
        print(json.dumps({"value": val, "unit": unit}))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()