#!/usr/bin/env python3
"""Run the repository's end-to-end engineering verification workflow."""

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = REPOSITORY_ROOT / "scripts"
REFERENCES_FILE = REPOSITORY_ROOT / "references" / "fluid_mechanics" / "references.json"
HEAT_TRANSFER_REFERENCES_FILE = REPOSITORY_ROOT / "references" / "heat_transfer" / "references.json"
REFERENCE_FILES = {
    "fluid_mechanics": REFERENCES_FILE,
    "heat_transfer": HEAT_TRANSFER_REFERENCES_FILE,
}

PROBLEM_DEFINITIONS = {
    "reynolds_number": {
        "name": "Reynolds Number",
        "reference": "reynolds_number",
        "equation": "Re = rho * V * D / mu",
        "expected": "dimensionless",
        "calculator": "reynolds_number",
        "result_key": "Reynolds_number",
        "required": [("rho", "V", "D", "mu"), ("V", "D", "nu")],
        "assumptions": ["continuum fluid", "Newtonian fluid", "constant properties"],
    },
    "pressure_drop": {
        "name": "Darcy-Weisbach Pressure Drop",
        "reference": "darcy_weisbach",
        "equation": "dP = f * (L / D) * (rho * V^2 / 2)",
        "expected": "Pa",
        "calculator": "pressure_drop",
        "result_key": "pressure_drop_Pa",
        "required": [("f", "L", "D", "rho", "V")],
        "assumptions": ["steady, incompressible flow", "fully developed flow", "constant Darcy friction factor"],
    },
    "bernoulli": {
        "name": "Bernoulli Equation",
        "reference": "bernoulli",
        "equation": "P2 = P1 + 0.5 * rho * (V1^2 - V2^2)",
        "expected": "Pa",
        "calculator": "bernoulli",
        "result_key": "pressure_2_Pa",
        "required": [("rho", "V1", "D1", "D2", "P1")],
        "assumptions": ["steady, incompressible flow", "horizontal pipe", "negligible friction losses"],
    },
    "mach_number": {
        "name": "Mach Number",
        "reference": "mach_number",
        "equation": "M = V / a",
        "expected": "dimensionless",
        "calculator": "mach_number",
        "result_key": "mach_number",
        "required": [("V", "a")],
        "assumptions": ["speed of sound is defined for the stated medium and conditions"],
    },
    "plane_wall_conduction": {
        "name": "Plane-Wall Conduction Heat Rate",
        "domain": "heat_transfer",
        "reference": "plane_wall_heat_rate",
        "equation": "Qdot = k*A*(T_hot-T_cold)/L",
        "expected": "W",
        "calculator": "plane_wall_conduction",
        "result_key": "heat_rate_W",
        "required": [("k", "A", "T_hot", "T_cold", "L")],
        "assumptions": ["steady state", "one-dimensional conduction", "constant conductivity", "no internal heat generation"],
    },
    "convective_heat_transfer": {
        "name": "Convective Heat Transfer Rate",
        "domain": "heat_transfer",
        "reference": "newton_cooling",
        "equation": "Qdot = h*A*(Ts-Tinf)",
        "expected": "W",
        "calculator": "convective_heat_transfer",
        "result_key": "heat_rate_W",
        "required": [("h_conv", "A", "Ts", "Tinf")],
        "assumptions": ["Newton law of cooling", "specified representative convection coefficient", "uniform surface temperature"],
    },
    "radiative_heat_transfer": {
        "name": "Radiative Heat Transfer to Large Surroundings",
        "domain": "heat_transfer",
        "reference": "stefan_boltzmann_net_large_surroundings",
        "equation": "Qdot = epsilon*sigma*A*(Ts^4-Tsur^4)",
        "expected": "W",
        "calculator": "radiative_heat_transfer",
        "result_key": "heat_rate_W",
        "required": [("emissivity", "A", "Ts", "Tsur")],
        "assumptions": ["opaque diffuse-gray surface", "large isothermal surroundings", "view factor approximately one", "absolute temperatures"],
    },
    "heat_exchanger_lmtd": {
        "name": "Heat-Exchanger LMTD Heat Rate",
        "domain": "heat_transfer",
        "reference": "lmtd_heat_exchanger",
        "equation": "Qdot = U*A*DTlm",
        "expected": "W",
        "calculator": "heat_exchanger_lmtd",
        "result_key": "heat_rate_W",
        "required": [("U_overall", "A", "DTlm")],
        "assumptions": ["steady operation", "supplied log-mean temperature difference includes any required correction factor", "overall coefficient and area use a consistent area basis"],
    },
}

INPUT_ALIASES = {
    "density": "rho", "rho": "rho",
    "dynamicviscosity": "mu", "mu": "mu",
    "kinematicviscosity": "nu", "nu": "nu",
    "velocity": "V", "v": "V",
    "diameter": "D", "pipediameter": "D", "d": "D",
    "frictionfactor": "f", "darcyfrictionfactor": "f", "f": "f",
    "pipelength": "L", "length": "L", "l": "L",
    "pressureatpoint1": "P1", "pressure1": "P1", "p1": "P1",
    "velocityatpoint1": "V1", "velocity1": "V1", "v1": "V1",
    "diameteratpoint1": "D1", "diameter1": "D1", "d1": "D1",
    "diameteratpoint2": "D2", "diameter2": "D2", "d2": "D2",
    "speedofsound": "a", "soundspeed": "a", "a": "a",
    "thermalconductivity": "k", "conductivity": "k", "k": "k",
    "area": "A", "surfacearea": "A", "heattransferarea": "A", "a": "a",
    "hottemperature": "T_hot", "hotsidetemperature": "T_hot", "thot": "T_hot",
    "coldtemperature": "T_cold", "coldsidetemperature": "T_cold", "tcold": "T_cold",
    "walltemperature": "Ts", "surfacetemperature": "Ts", "ts": "Ts",
    "ambienttemperature": "Tinf", "fluidtemperature": "Tinf", "tinf": "Tinf",
    "surroundingstemperature": "Tsur", "surroundingtemperature": "Tsur", "tsur": "Tsur",
    "emissivity": "emissivity", "epsilon": "emissivity",
    "convectioncoefficient": "h_conv", "heattransfercoefficient": "h_conv", "hconv": "h_conv",
    "overallheattransfercoefficient": "U_overall", "overallcoefficient": "U_overall", "uoverall": "U_overall",
    "logmeantemperaturedifference": "DTlm", "correctedlogmeantemperaturedifference": "DTlm", "dtlm": "DTlm",
    "wallthickness": "L", "thickness": "L",
}
DIMENSIONLESS_INPUTS = {"f", "emissivity"}
INPUT_SI_UNITS = {
    "k": "watt / meter / kelvin",
    "h_conv": "watt / meter ** 2 / kelvin",
    "U_overall": "watt / meter ** 2 / kelvin",
    "A": "meter ** 2",
    "L": "meter",
    "T_hot": "kelvin", "T_cold": "kelvin", "Ts": "kelvin",
    "Tinf": "kelvin", "Tsur": "kelvin", "DTlm": "delta_kelvin",
}
SUPERSCRIPTS = str.maketrans({"⁰": "0", "¹": "1", "²": "2", "³": "3",
                              "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7",
                              "⁸": "8", "⁹": "9", "⁻": "-", "⁺": "+",
                              "₀": "0", "₁": "1", "₂": "2"})


def canonical_input_name(label: str) -> Optional[str]:
    normalized = label.translate(SUPERSCRIPTS).lower()
    normalized = normalized.replace("ρ", "rho").replace("μ", "mu").replace("ν", "nu")
    normalized = re.sub(r"[^a-z0-9]", "", normalized)
    if normalized in INPUT_ALIASES:
        return INPUT_ALIASES[normalized]
    if "overallheattransfercoefficient" in normalized or "overallcoefficient" in normalized:
        return "U_overall"
    if "thermalconductivity" in normalized:
        return "k"
    if "emissivity" in normalized:
        return "emissivity"
    if "convectioncoefficient" in normalized or "heattransfercoefficient" in normalized:
        return "h_conv"
    if "surroundingstemperature" in normalized or "surroundingtemperature" in normalized:
        return "Tsur"
    if "ambienttemperature" in normalized or "fluidtemperature" in normalized:
        return "Tinf"
    if "walltemperature" in normalized or "surfacetemperature" in normalized:
        return "Ts"
    if "hottemperature" in normalized or "hotsidetemperature" in normalized:
        return "T_hot"
    if "coldtemperature" in normalized or "coldsidetemperature" in normalized:
        return "T_cold"
    if "logmeantemperaturedifference" in normalized:
        return "DTlm"
    if "surfacearea" in normalized or "heattransferarea" in normalized:
        return "A"
    # Prefer point-specific forms before the generic quantity names.
    for phrase, canonical in (
        ("velocityatpoint1", "V1"), ("diameteratpoint1", "D1"),
        ("diameteratpoint2", "D2"), ("pressureatpoint1", "P1"),
    ):
        if phrase in normalized:
            return canonical
    if "dynamicviscosity" in normalized:
        return "mu"
    if "kinematicviscosity" in normalized:
        return "nu"
    if "density" in normalized:
        return "rho"
    if "frictionfactor" in normalized:
        return "f"
    if "speedofsound" in normalized:
        return "a"
    if "velocity" in normalized and "point1" not in normalized:
        return "V"
    if "diameter" in normalized and "point" not in normalized:
        return "D"
    if "pipelength" in normalized:
        return "L"
    return None


def parse_quantity(text: str) -> Optional[Tuple[float, str]]:
    text = text.replace("**", "").strip().translate(SUPERSCRIPTS)
    match = re.match(
        r"^\s*(?P<number>[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?)"
        r"(?:\s*[×x]\s*10\s*\^?\s*(?P<power>[+-]?\d+))?\s*(?P<unit>[^\s()]+)?",
        text,
    )
    if not match:
        return None
    value = float(match.group("number").replace(",", ""))
    if match.group("power"):
        value *= 10 ** int(match.group("power"))
    return value, (match.group("unit") or "").rstrip(",")


def normalize_unit(unit: str) -> str:
    unit = unit.translate(SUPERSCRIPTS).replace("·", "*").replace("μ", "micro")
    unit = re.sub(r"(?<=[A-Za-z])([23])(?=\b|/)", r"**\1", unit)
    unit = unit.replace("m3", "m**3").replace("m2", "m**2")
    unit = unit.replace("Pa*s", "Pa * s")
    return unit


class VerificationEngine:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def run_tool(self, tool: str, args: List[str]) -> Dict[str, Any]:
        script_path = SCRIPTS_DIR / f"{tool}.py"
        if not script_path.is_file():
            return {"error": f"Required tool not found: {script_path}"}
        command = [sys.executable, str(script_path), *args]
        if self.verbose:
            print(f"Running: {' '.join(command)}", file=sys.stderr)
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return {"error": f"Tool timed out: {tool}"}
        except OSError as exc:
            return {"error": f"Could not run {tool}: {exc}"}
        output = result.stdout.strip()
        if output:
            try:
                parsed = json.loads(output)
                if result.returncode and isinstance(parsed, dict):
                    parsed.setdefault("returncode", result.returncode)
                return parsed
            except json.JSONDecodeError:
                return {"error": result.stderr.strip() or output, "returncode": result.returncode}
        return {"error": result.stderr.strip() or f"{tool} returned no output", "returncode": result.returncode}

    def detect_problem(self, text: str) -> Optional[str]:
        lowered = text.lower()
        if "heat exchanger" in lowered or "heat-exchanger" in lowered or "lmtd" in lowered:
            return "heat_exchanger_lmtd"
        if "radiation" in lowered or "radiative" in lowered or "emissivity" in lowered:
            return "radiative_heat_transfer"
        if "convection" in lowered or "convective" in lowered or "newton's law of cooling" in lowered:
            return "convective_heat_transfer"
        if "plane-wall conduction" in lowered or "plane wall conduction" in lowered or "fourier conduction" in lowered:
            return "plane_wall_conduction"
        if "reynolds" in lowered:
            return "reynolds_number"
        if "bernoulli" in lowered:
            return "bernoulli"
        if "darcy" in lowered or "pressure drop" in lowered:
            return "pressure_drop"
        if "mach number" in lowered or re.search(r"\bmach\b", lowered):
            return "mach_number"
        return None

    def parse_problem(self, text: str, problem_type: str) -> Tuple[Dict[str, Dict[str, Any]], Optional[Dict[str, Any]]]:
        knowns: Dict[str, Dict[str, Any]] = {}
        in_reported_section = False
        reported = None
        definition = PROBLEM_DEFINITIONS[problem_type]

        for line in text.splitlines():
            heading = re.match(r"^\s*#{1,6}\s+(.+?)\s*$", line)
            if heading:
                in_reported_section = "reported result" in heading.group(1).lower()
            if in_reported_section:
                match = re.match(r"^\s*([^=]+?)\s*=\s*(.+?)\s*$", line)
                if match:
                    symbol = match.group(1).strip().translate(SUPERSCRIPTS).lower()
                    quantity = parse_quantity(match.group(2))
                    if quantity:
                        if symbol.startswith("re") or "reynolds" in symbol:
                            key = "Reynolds_number"
                        elif symbol.startswith("δp") or symbol.startswith("Δp".lower()) or "pressure drop" in symbol:
                            key = "pressure_drop_Pa"
                        elif symbol.startswith("p2") or symbol.startswith("p₂"):
                            key = "pressure_2_Pa"
                        elif symbol == "m" or "mach" in symbol:
                            key = "mach_number"
                        else:
                            key = definition["result_key"]
                        value, unit = quantity
                        if unit.lower() == "kpa":
                            value *= 1000.0
                            unit = "Pa (converted from kPa)"
                        elif unit.lower() == "kw":
                            value *= 1000.0
                            unit = "W (converted from kW)"
                        reported = {"key": key, "value": value, "unit": unit or "SI"}
                        break
                continue

            label_value = re.match(r"^\s*[-*]\s*([^:]+?)\s*:\s*(.*?)\s*$", line)
            if not label_value:
                continue
            canonical = canonical_input_name(label_value.group(1))
            if canonical is None:
                continue
            quantity = parse_quantity(label_value.group(2))
            if quantity:
                value, unit = quantity
                knowns[canonical] = {"value": value, "unit": normalize_unit(unit), "label": label_value.group(1).strip()}

        return knowns, reported

    def convert_inputs(self, knowns: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, float], List[str]]:
        si_values: Dict[str, float] = {}
        issues: List[str] = []
        for name, quantity in knowns.items():
            value = quantity["value"]
            unit = quantity["unit"]
            if name in DIMENSIONLESS_INPUTS:
                if unit in ("", "1", "dimensionless"):
                    si_values[name] = value
                elif unit in ("%", "percent"):
                    si_values[name] = value / 100.0
                else:
                    issues.append(f"{name}: expected a dimensionless value, got '{unit}'")
                continue
            if not unit:
                issues.append(f"{name}: unit is missing")
                continue
            if name in INPUT_SI_UNITS:
                result = self.run_tool("units", [
                    "convert", "--value", str(value), "--from", unit, "--to", INPUT_SI_UNITS[name],
                ])
                if isinstance(result, (int, float)):
                    si_values[name] = float(result)
                elif "error" in result:
                    issues.append(f"{name}: {result['error']}")
                else:
                    issues.append(f"{name}: unit conversion did not return a number")
                continue
            result = self.run_tool("units", ["si", "--value", str(value), "--unit", unit])
            if "error" in result or "value" not in result:
                issues.append(f"{name}: {result.get('error', 'unit conversion failed')}")
                continue
            si_values[name] = float(result["value"])
        return si_values, issues

    def load_references(self, domain: str = "fluid_mechanics") -> Dict[str, Any]:
        def reject_duplicates(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"Duplicate reference key: {key}")
                result[key] = value
            return result

        reference_file = REFERENCE_FILES.get(domain)
        if reference_file is None:
            raise ValueError(f"Unknown reference domain '{domain}'")
        with reference_file.open(encoding="utf-8") as handle:
            data = json.load(handle, object_pairs_hook=reject_duplicates)
        if not isinstance(data, dict):
            raise ValueError("Reference database root must be an object")
        if domain == "heat_transfer":
            metadata = data.get("metadata", {})
            sources = metadata.get("sources", {})
            equations = data.get("equations", {})
            if not isinstance(sources, dict) or not isinstance(equations, dict):
                raise ValueError("Heat-transfer reference must contain source and equation objects")
            normalized = {}
            for key, item in equations.items():
                if not isinstance(item, dict) or not isinstance(item.get("equation"), str):
                    raise ValueError(f"Heat-transfer reference '{key}' must include an equation string")
                source = sources.get(item.get("source"))
                if not isinstance(source, dict) or not isinstance(source.get("title"), str):
                    raise ValueError(f"Heat-transfer reference '{key}' has no valid source record")
                assumptions = item.get("assumptions", [])
                if not isinstance(assumptions, list):
                    raise ValueError(f"Heat-transfer reference '{key}' assumptions must be a list")
                normalized[key] = {
                    "equation": item["equation"],
                    "sources": [source],
                    "assumptions": assumptions,
                }
            return normalized
        for key, item in data.items():
            if not isinstance(item, dict) or not isinstance(item.get("equation"), str):
                raise ValueError(f"Reference '{key}' must include an equation string")
            if not isinstance(item.get("sources", []), list) or not isinstance(item.get("assumptions", []), list):
                raise ValueError(f"Reference '{key}' sources and assumptions must be lists")
            for source in item.get("sources", []):
                if not isinstance(source, dict) or not isinstance(source.get("title"), str):
                    raise ValueError(f"Reference '{key}' contains a source without a title")
        return data

    def check_reference(self, reference_id: str, domain: str = "fluid_mechanics") -> Dict[str, Any]:
        try:
            data = self.load_references(domain)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            return {"status": "FAIL", "error": str(exc)}
        item = data.get(reference_id)
        if item is None:
            return {"status": "FAIL", "error": f"No reference entry for '{reference_id}'"}
        sources = item.get("sources", [])
        if not sources:
            return {"status": "FAIL", "error": f"Reference '{reference_id}' has no source records"}
        return {
            "status": "PASS",
            "reference": reference_id,
            "equation": item["equation"],
            "sources_count": len(sources),
            "assumptions": item.get("assumptions", []),
        }

    def verify(self, problem_file: Optional[str] = None, problem_text: Optional[str] = None,
               reported_value: Optional[float] = None, tolerance: float = 0.01) -> Dict[str, Any]:
        if problem_file:
            try:
                problem_text = Path(problem_file).read_text(encoding="utf-8")
            except OSError as exc:
                return self.failure_result(f"Could not read problem file: {exc}")
        if problem_text is None:
            return self.failure_result("A problem file or problem text is required")

        problem_type = self.detect_problem(problem_text)
        if problem_type is None:
            return self.failure_result("The problem type is not supported by the end-to-end verifier")

        definition = PROBLEM_DEFINITIONS[problem_type]
        knowns, parsed_report = self.parse_problem(problem_text, problem_type)
        si_inputs, unit_issues = self.convert_inputs(knowns)
        input_issues = self.validate_inputs(problem_type, si_inputs)
        if problem_type == "reynolds_number":
            missing = [name for name in ("V", "D") if name not in si_inputs]
            if "rho" not in si_inputs and "nu" not in si_inputs:
                missing.append("rho or nu")
            if "mu" not in si_inputs and "nu" not in si_inputs:
                missing.append("mu or nu")
        else:
            required = definition["required"][0]
            missing = [name for name in required if name not in si_inputs]

        dimensional_args = [
            "--equation", definition["equation"], "--expected", definition["expected"],
        ]
        if definition.get("domain"):
            dimensional_args.extend(["--domain", definition["domain"]])
        dimensional_args.append("--verbose")
        dimensional = self.run_tool("dimensional_check", dimensional_args)
        dimensional["status"] = "PASS" if dimensional.get("match") else "FAIL"

        reference = self.check_reference(definition["reference"], definition.get("domain", "fluid_mechanics"))
        calculation: Dict[str, Any] = {}
        if not missing and not unit_issues and not input_issues:
            calculation = self.run_tool("calculate", [
                "--problem", definition["calculator"], "--inputs", json.dumps(si_inputs),
            ])
        elif missing:
            calculation = {"status": "SKIPPED", "reason": "Required inputs are missing"}
        elif unit_issues:
            calculation = {"status": "SKIPPED", "reason": "One or more input units could not be converted"}
        else:
            calculation = {"status": "SKIPPED", "reason": "One or more input values are physically invalid"}

        if calculation and calculation.get("status") != "SKIPPED" and "error" not in calculation:
            calculation["status"] = "PASS"
        elif "error" in calculation:
            calculation["status"] = "FAIL"

        reported = ({"key": definition["result_key"], "value": float(reported_value), "unit": "SI override"}
                    if reported_value is not None else parsed_report)
        computed = calculation.get(definition["result_key"])

        comparison: Dict[str, Any]
        if reported is None:
            comparison = {"status": "SKIPPED", "reason": "No reported result was provided"}
        elif reported["key"] != definition["result_key"]:
            comparison = {"status": "FAIL", "error": f"Reported result key '{reported['key']}' does not match '{definition['result_key']}'"}
        elif computed is None:
            comparison = {"status": "SKIPPED", "reason": "No computed result is available"}
        else:
            comparison = self.run_tool("compare", [
                "--computed", str(computed), "--reported", str(reported["value"]), "--tolerance", str(tolerance),
            ])
            comparison["status"] = "PASS" if comparison.get("passed") else "FAIL"

        sanity = self.physical_sanity(problem_type, calculation, si_inputs)
        unit_check = {"status": "FAIL" if unit_issues else "PASS", "si_values": si_inputs, "issues": unit_issues}
        if missing:
            unit_check["missing_required_inputs"] = missing
        input_validation = {"status": "FAIL" if input_issues else "PASS", "issues": input_issues}

        if missing or unit_issues or not reported or reference["status"] != "PASS":
            verdict = "INSUFFICIENT INFORMATION"
        elif input_issues or "error" in calculation or dimensional["status"] == "FAIL" or sanity["status"] == "FAIL" or comparison["status"] == "FAIL":
            verdict = "NOT VERIFIED"
        else:
            verdict = "VERIFIED"

        confidence = "HIGH" if verdict == "VERIFIED" else ("MEDIUM" if verdict == "NOT VERIFIED" and computed is not None else "LOW")
        result = {
            "problem_type": problem_type,
            "problem_summary": problem_text[:200],
            "equation": definition["equation"],
            "assumptions": definition["assumptions"],
            "unit_check": unit_check,
            "input_validation": input_validation,
            "dimensional_check": dimensional,
            "calculation": calculation,
            "reference_check": reference,
            "sanity_check": sanity,
            "reported_result": reported,
            "comparison": comparison,
            "missing_inputs": missing,
            "verdict": verdict,
            "confidence": confidence,
        }
        result["report"] = self.format_report(result)
        return result

    @staticmethod
    def validate_inputs(problem_type: str, inputs: Dict[str, float]) -> List[str]:
        issues = [f"{name} must be finite" for name, value in inputs.items() if not math.isfinite(value)]
        strictly_positive = {
            "reynolds_number": ("rho", "D"),
            "pressure_drop": ("rho", "D"),
            "bernoulli": ("rho", "D1", "D2"),
            "mach_number": ("a",),
            "plane_wall_conduction": ("k", "A", "L"),
            "convective_heat_transfer": ("h_conv", "A"),
            "radiative_heat_transfer": ("A", "Ts", "Tsur"),
            "heat_exchanger_lmtd": ("U_overall", "A", "DTlm"),
        }[problem_type]
        for name in strictly_positive:
            if name in inputs and inputs[name] <= 0:
                issues.append(f"{name} must be greater than zero")

        non_negative = {
            "reynolds_number": ("V",),
            "pressure_drop": ("V", "L", "f"),
            "bernoulli": ("V1",),
            "mach_number": ("V",),
            "plane_wall_conduction": (),
            "convective_heat_transfer": (),
            "radiative_heat_transfer": (),
            "heat_exchanger_lmtd": (),
        }[problem_type]
        for name in non_negative:
            if name in inputs and inputs[name] < 0:
                issues.append(f"{name} must be non-negative")

        if problem_type == "reynolds_number":
            for name in ("mu", "nu"):
                if name in inputs and inputs[name] == 0:
                    issues.append(f"{name} must be greater than zero")
        for name in ("T_hot", "T_cold", "Ts", "Tinf", "Tsur"):
            if name in inputs and inputs[name] < 0:
                issues.append(f"{name} must be a non-negative absolute temperature")
        if problem_type == "radiative_heat_transfer" and "emissivity" in inputs:
            if not 0 <= inputs["emissivity"] <= 1:
                issues.append("emissivity must be between zero and one")
        return issues

    @staticmethod
    def physical_sanity(problem_type: str, calculation: Dict[str, Any], inputs: Dict[str, float]) -> Dict[str, Any]:
        if calculation.get("status") == "SKIPPED":
            return {"status": "SKIPPED", "checks": [], "issues": [], "reason": calculation.get("reason")}
        if "error" in calculation or not calculation:
            return {"status": "SKIPPED", "checks": [], "issues": ["No calculation result is available"]}
        checks: List[str] = []
        issues: List[str] = []
        if problem_type == "reynolds_number":
            reynolds = calculation.get("Reynolds_number")
            if reynolds is None or not math.isfinite(reynolds) or reynolds < 0:
                issues.append("Reynolds number must be non-negative and finite")
            else:
                checks.append(f"Positive finite Reynolds number ({reynolds:.6g})")
        elif problem_type == "pressure_drop":
            pressure_drop = calculation.get("pressure_drop_Pa")
            if pressure_drop is None or not math.isfinite(pressure_drop) or pressure_drop < 0:
                issues.append("Pressure drop must be finite and non-negative")
            else:
                checks.append(f"Finite non-negative pressure drop ({pressure_drop:.6g} Pa)")
        elif problem_type == "bernoulli":
            velocity_2 = calculation.get("velocity_2_m_s")
            pressure_2 = calculation.get("pressure_2_Pa")
            if velocity_2 is None or not math.isfinite(velocity_2) or velocity_2 < 0:
                issues.append("Calculated downstream velocity is not physically meaningful")
            else:
                checks.append(f"Finite downstream velocity ({velocity_2:.6g} m/s)")
            if pressure_2 is None or not math.isfinite(pressure_2):
                issues.append("Calculated downstream pressure is not finite")
            else:
                checks.append(f"Finite downstream pressure ({pressure_2:.6g} Pa)")
        elif problem_type == "mach_number":
            mach = calculation.get("mach_number")
            if mach is None or not math.isfinite(mach) or mach < 0:
                issues.append("Mach number must be finite and non-negative")
            else:
                checks.append(f"Finite non-negative Mach number ({mach:.6g})")
        elif problem_type in {
            "plane_wall_conduction", "convective_heat_transfer",
            "radiative_heat_transfer", "heat_exchanger_lmtd",
        }:
            heat_rate = calculation.get("heat_rate_W")
            if heat_rate is None or not math.isfinite(heat_rate):
                issues.append("Calculated heat-transfer rate must be finite")
            else:
                checks.append(f"Finite heat-transfer rate ({heat_rate:.6g} W)")
                if problem_type == "plane_wall_conduction":
                    expected_sign = inputs["T_hot"] - inputs["T_cold"]
                elif problem_type == "convective_heat_transfer":
                    expected_sign = inputs["Ts"] - inputs["Tinf"]
                elif problem_type == "radiative_heat_transfer":
                    expected_sign = inputs["Ts"] - inputs["Tsur"]
                else:
                    expected_sign = 1
                if heat_rate * expected_sign < 0:
                    issues.append("Heat-transfer rate sign conflicts with the temperature driving force")
        return {"status": "FAIL" if issues else "PASS", "checks": checks, "issues": issues}

    @staticmethod
    def format_report(result: Dict[str, Any]) -> str:
        lines = [
            "ENGINEERING VERIFICATION REPORT",
            "================================",
            f"Problem type: {result['problem_type']}",
            f"Governing equation: {result['equation']}",
            f"Assumptions: {', '.join(result['assumptions'])}",
            "",
        ]
        for name in ("unit_check", "input_validation", "dimensional_check", "calculation", "reference_check", "sanity_check", "comparison"):
            item = result[name]
            lines.append(f"{name.replace('_', ' ').title()}: {item.get('status', 'N/A')}")
            for detail in item.get("issues", []):
                lines.append(f"  - {detail}")
            if item.get("error"):
                lines.append(f"  - Error: {item['error']}")
            if item.get("reason"):
                lines.append(f"  - {item['reason']}")
        if result["missing_inputs"]:
            lines.append("Missing inputs: " + ", ".join(result["missing_inputs"]))
        if result.get("reported_result"):
            lines.append(f"Reported result: {result['reported_result']['value']} {result['reported_result']['unit']}")
        lines.extend(["", f"Overall verdict: {result['verdict']}", f"Confidence: {result['confidence']}"])
        return "\n".join(lines)

    @staticmethod
    def failure_result(message: str) -> Dict[str, Any]:
        report = f"ENGINEERING VERIFICATION REPORT\n================================\n\nINSUFFICIENT INFORMATION\n{message}"
        return {"verdict": "INSUFFICIENT INFORMATION", "confidence": "LOW", "error": message, "report": report}


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a supported engineering calculation")
    parser.add_argument("--problem-file", help="Path to a problem Markdown file")
    parser.add_argument("--reported-value", type=float, help="Reported result in SI units (overrides the file)")
    parser.add_argument("--tolerance", type=float, default=0.01, help="Relative comparison tolerance")
    parser.add_argument("--output", choices=("json", "markdown", "text"), default="markdown")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not 0 <= args.tolerance:
        parser.error("--tolerance must be non-negative")
    result = VerificationEngine(verbose=args.verbose).verify(
        problem_file=args.problem_file, reported_value=args.reported_value, tolerance=args.tolerance,
    )
    print(json.dumps(result, indent=2) if args.output == "json" else result.get("report", "No report generated"))
    sys.exit({"VERIFIED": 0, "NOT VERIFIED": 1, "INSUFFICIENT INFORMATION": 2}.get(result.get("verdict"), 2))


if __name__ == "__main__":
    main()
