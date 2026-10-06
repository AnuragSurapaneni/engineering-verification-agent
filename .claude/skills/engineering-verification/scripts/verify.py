#!/usr/bin/env python3
"""
Verify command for engineering-verification Skill.

Runs the full 10-step verification workflow on a problem.
Can be invoked with a problem file or from conversation context.

Usage:
    python verify.py --problem-file examples/reynolds_number.md
    python verify.py --problem-file examples/pressure_drop.md --reported-value '{"pressure_drop_Pa": 7976}'
    python verify.py --problem-file examples/bernoulli.md --tolerance 0.02
"""

import sys
import json
import argparse
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import re

# Add the Skill directory to path for imports
SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
REFERENCES_DIR = SKILL_DIR / "references"


class VerificationEngine:
    """Orchestrates the 10-step verification workflow."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}

    def run_tool(self, tool: str, args: List[str]) -> Dict[str, Any]:
        """Run a Python tool script and return parsed JSON output."""
        script_path = SCRIPTS_DIR / f"{tool}.py"
        cmd = [sys.executable, str(script_path)] + args

        if self.verbose:
            print(f"  Running: {' '.join(cmd)}", file=sys.stderr)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return {"error": result.stderr, "returncode": result.returncode}

            # Try to parse JSON output
            output = result.stdout.strip()
            if output:
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"raw_output": output}
            return {}
        except subprocess.TimeoutExpired:
            return {"error": "Tool timed out"}
        except Exception as e:
            return {"error": str(e)}

    def step1_understand_problem(self, problem_text: str) -> Dict[str, Any]:
        """Step 1: Parse problem and extract knowns/unknowns."""
        # Extract quantities with units
        knowns = {}
        reported = {}

        lines = problem_text.split('\n')

        for line in lines:
            stripped = line.strip()

            # Match "Name: value unit" format (with optional leading "-") e.g., "- Temperature: 300 K"
            m = re.match(r'^(-?\s*)([A-Za-z][A-Za-z\s]*)\s*:\s*([\d\.eE\-\+]+)\s*([A-Za-z/\.\-]*)', stripped)
            if m:
                name = m.group(2).strip()
                try:
                    value = float(m.group(3))
                    unit = m.group(4).strip()
                    if name and value > 0:
                        knowns[name] = {"value": value, "unit": unit}
                except ValueError:
                    pass

            # Match markdown list items with quantities: "- Temperature: 300 K"
            if stripped.startswith('-') and ':' in stripped:
                m = re.search(r':\s*([\d\.eE\-\+]+)\s*([A-Za-z/]+)', stripped)
                if m:
                    try:
                        value = float(m.group(1))
                        unit = m.group(2)
                        name = stripped.split(':')[0].strip('-').strip()
                        knowns[name] = {"value": value, "unit": unit}
                    except ValueError:
                        pass

            # Match "## Fluid Properties" section headers
            if re.search(r'##\s*Fluid Properties', stripped, re.IGNORECASE):
                continue  # Handled by quantity parsing above

            # Match "## Reported Result" section
            if re.search(r'##\s*Reported Result', stripped, re.IGNORECASE):
                # Next lines will contain the reported value - handled by pattern matching below
                continue

        # Extract reported values from "## Reported Result" section
        reported_patterns = [
            r'##\s*Reported Result\s*\n\s*Re\s*[=:]\s*([\d\.]+)',
            r'##\s*Reported Result\s*\n\s*ΔP\s*[=:]\s*([\d\.]+)\s*(kPa|Pa)?',
            r'##\s*Reported Result\s*\n\s*Reynolds number\s*[=:]\s*([\d\.]+)',
        ]
        for pattern in reported_patterns:
            for match in re.finditer(pattern, problem_text, re.IGNORECASE):
                val_str = match.group(1)
                try:
                    reported["Re"] = float(val_str)
                except ValueError:
                    pass

        # If no reported value found in structured section, check last part of problem text
        if "Re" not in reported:
            last_section_match = re.search(r'Re\s*[=:]\s*([\d\.]+)\s*\((\w+)\)', problem_text[-500:], re.IGNORECASE)
            if last_section_match:
                try:
                    reported["Re"] = float(last_section_match.group(1))
                except ValueError:
                    pass

        return {
            "knowns": knowns,
            "reported": reported,
            "raw_text": problem_text[:500]
        }

    def step2_extract_equations(self, problem_text: str) -> Dict[str, Any]:
        """Step 2: Identify governing equations from problem context."""
        equations = {}

        # Detect problem type from keywords
        text_lower = problem_text.lower()

        if "reynolds" in text_lower:
            equations["primary"] = {
                "name": "Reynolds Number",
                "formula": "Re = rho * V * D / mu",
                "alternate": "Re = V * D / nu",
                "variables": ["rho", "V", "D", "mu"],
                "output": "Re"
            }
        elif "darcy" in text_lower or "pressure drop" in text_lower:
            equations["primary"] = {
                "name": "Darcy-Weisbach Pressure Drop",
                "formula": "ΔP = f * (L/D) * (rho * V^2 / 2)",
                "variables": ["f", "L", "D", "rho", "V"],
                "output": "ΔP"
            }
        elif "bernoulli" in text_lower:
            equations["primary"] = {
                "name": "Bernoulli Equation",
                "formula": "P1/rho + V1^2/2 + g*z1 = P2/rho + V2^2/2 + g*z2",
                "variables": ["rho", "V1", "D1", "D2", "P1"],
                "output": "P2"
            }

        return equations

    def step3_identify_assumptions(self, problem_text: str) -> List[str]:
        """Step 3: Extract assumptions from problem."""
        assumptions = []

        # Default assumptions based on domain
        text_lower = problem_text.lower()

        if "reynolds" in text_lower:
            assumptions.extend([
                "continuum hypothesis",
                "newtonian fluid",
                "constant properties",
                "fully developed flow"
            ])
        elif "pressure drop" in text_lower or "darcy" in text_lower:
            assumptions.extend([
                "steady, incompressible flow",
                "fully developed flow",
                "constant cross-section circular pipe",
                "constant friction factor along pipe length"
            ])
        elif "bernoulli" in text_lower:
            assumptions.extend([
                "steady flow",
                "incompressible flow",
                "inviscid (no friction losses)",
                "along a streamline",
                "no shaft work (pumps/turbines)",
                "no heat transfer"
            ])

        # Look for explicit assumptions in text
        if "assum" in text_lower:
            # Could parse explicit assumptions here
            pass

        return assumptions

    def step4_check_units(self, knowns: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Verify unit consistency using units.py."""
        # Convert all to SI using units.py
        si_values = {}
        issues = []

        for name, data in knowns.items():
            value = data["value"]
            unit = data["unit"]
            try:
                result = self.run_tool("units", ["si", "--value", str(value), "--unit", unit])
                if "error" not in result:
                    si_values[name] = {"value": result["value"], "unit": result["unit"]}
                else:
                    issues.append(f"{name}: {result['error']}")
            except Exception as e:
                issues.append(f"{name}: {e}")

        return {
            "si_values": si_values,
            "issues": issues,
            "status": "PASS" if not issues else "FAIL"
        }

    def step5_check_dimensions(self, equation: str, expected_output: str) -> Dict[str, Any]:
        """Step 5: Dimensional analysis using dimensional_check.py."""
        result = self.run_tool("dimensional_check", [
            "--equation", equation,
            "--expected", expected_output
        ])
        result["status"] = "PASS" if result.get("match", False) else "FAIL"
        return result

    def step6_independent_calculation(self, problem_type: str, inputs: Dict[str, float]) -> Dict[str, Any]:
        """Step 6: Run numerical calculation using calculate.py."""
        # Map problem type to calculator
        type_map = {
            "reynolds": "reynolds_number",
            "reynolds_number": "reynolds_number",
            "pressure_drop": "pressure_drop",
            "darcy": "pressure_drop",
            "darcy_weisbach": "pressure_drop",
            "bernoulli": "bernoulli"
        }

        calc_type = type_map.get(problem_type, problem_type)

        # Convert inputs dict to JSON string
        inputs_json = json.dumps(inputs)

        result = self.run_tool("calculate", [
            "--problem", calc_type,
            "--inputs", inputs_json
        ])

        return result

    def step7_reference_verification(self, equation_name: str) -> Dict[str, Any]:
        """Step 7: Cross-check against references.json."""
        ref_file = REFERENCES_DIR / "fluid_mechanics" / "references.json"

        if not ref_file.exists():
            return {"status": "WARNING", "message": "References file not found"}

        try:
            with open(ref_file) as f:
                refs = json.load(f)

            # Find matching reference
            ref_key = None
            for key in refs:
                if equation_name.lower().replace(" ", "_") in key.lower():
                    ref_key = key
                    break

            if ref_key:
                ref = refs[ref_key]
                return {
                    "status": "PASS",
                    "reference": ref_key,
                    "sources_count": len(ref.get("sources", [])),
                    "assumptions": ref.get("assumptions", [])
                }
            else:
                return {"status": "WARNING", "message": f"No reference found for {equation_name}"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    def step8_physical_sanity_checks(self, problem_type: str, result: Dict[str, Any],
                                      inputs: Dict[str, float]) -> Dict[str, Any]:
        """Step 8: Physical sanity checks."""
        checks = []
        issues = []

        if problem_type == "reynolds_number":
            Re = result.get("Reynolds_number", 0)
            checks.append(f"Re = {Re:.0f}")
            if Re > 0:
                checks.append("Re > 0 (physically meaningful)")
            if Re > 4000:
                checks.append("Turbulent regime (Re > 4000)")
            elif Re < 2300:
                checks.append("Laminar regime (Re < 2300)")
            else:
                checks.append("Transitional regime")

        elif problem_type == "pressure_drop":
            dP = result.get("pressure_drop_Pa", 0)
            checks.append(f"ΔP = {dP:.1f} Pa")
            if dP > 0:
                checks.append("Positive pressure drop (correct sign)")
            else:
                issues.append("Negative pressure drop (incorrect sign)")

            # Check V^2 relationship
            if "V" in inputs and "rho" in inputs and "f" in inputs and "L" in inputs and "D" in inputs:
                expected_order = inputs["f"] * (inputs["L"]/inputs["D"]) * (inputs["rho"] * inputs["V"]**2 / 2)
                ratio = dP / expected_order if expected_order != 0 else 0
                if 0.5 < ratio < 2.0:
                    checks.append("Magnitude consistent with V^2 scaling")
                else:
                    issues.append(f"Magnitude unexpected (ratio: {ratio:.2f})")

        elif problem_type == "bernoulli":
            P2 = result.get("pressure_2_Pa", 0)
            V2 = result.get("velocity_2_m_s", 0)
            V1 = inputs.get("V1", 0)
            checks.append(f"P2 = {P2/1000:.1f} kPa")
            checks.append(f"V2 = {V2:.1f} m/s")
            if V2 > V1:
                checks.append("Velocity increases as diameter decreases (continuity)")
            if P2 < inputs.get("P1", 0):
                checks.append("Pressure decreases as velocity increases (Venturi effect)")
            else:
                issues.append("Pressure should decrease when velocity increases")

        return {
            "checks": checks,
            "issues": issues,
            "status": "PASS" if not issues else "FAIL"
        }

    def step9_compare_results(self, computed: float, reported: float, tolerance: float = 0.01) -> Dict[str, Any]:
        """Step 9: Compare computed vs reported using compare.py."""
        result = self.run_tool("compare", [
            "--computed", str(computed),
            "--reported", str(reported),
            "--tolerance", str(tolerance)
        ])
        result["status"] = "PASS" if result.get("passed", False) else "FAIL"
        return result

    def step10_generate_report(self, problem_text: str, all_results: Dict[str, Any]) -> str:
        """Step 10: Generate structured verification report."""
        report = []
        report.append("ENGINEERING VERIFICATION REPORT")
        report.append("=" * 40)
        report.append("")

        # Problem summary
        report.append(f"Problem: {all_results.get('problem_summary', 'Engineering calculation')}")
        report.append(f"Governing Equation: {all_results.get('equation', {}).get('formula', 'N/A')}")
        report.append(f"Assumptions: {', '.join(all_results.get('assumptions', []))}")
        report.append("")

        # Check results
        checks = [
            ("Dimensional Check", all_results.get("dimensional_check", {})),
            ("Unit Consistency", all_results.get("unit_check", {})),
            ("Independent Calculation", all_results.get("calculation", {})),
            ("Reference Check", all_results.get("reference_check", {})),
            ("Physical Sanity Check", all_results.get("sanity_check", {})),
            ("Comparison with Reported", all_results.get("comparison", {})),
        ]

        for name, result in checks:
            status = result.get("status", "N/A")
            report.append(f"{name}: {status}")

        report.append("")

        # Overall verdict
        verdict = all_results.get("verdict", "INSUFFICIENT INFORMATION")
        confidence = all_results.get("confidence", "LOW")
        report.append(f"Overall Verdict: {verdict}")
        report.append(f"Confidence: {confidence}")

        return "\n".join(report)

    def verify(self, problem_file: Optional[str] = None, problem_text: Optional[str] = None,
               reported_value: Optional[float] = None, tolerance: float = 0.01) -> Dict[str, Any]:
        """Run full verification workflow."""

        # Get problem text
        if problem_file:
            with open(problem_file) as f:
                problem_text = f.read()
        elif problem_text is None:
            return {"error": "Either problem_file or problem_text must be provided"}

        # Step 1: Understand problem
        problem_data = self.step1_understand_problem(problem_text)
        knowns = problem_data["knowns"]
        reported = problem_data["reported"]

        # Step 2: Extract equations
        equations = self.step2_extract_equations(problem_text)
        primary_eq = equations.get("primary", {})
        problem_type = primary_eq.get("name", "").lower().replace(" ", "_")

        # Step 3: Identify assumptions
        assumptions = self.step3_identify_assumptions(problem_text)

        # Step 4: Check units
        unit_check = self.step4_check_units(knowns)

        # Step 5: Check dimensions
        eq_formula = primary_eq.get("formula", "")
        expected_dim = primary_eq.get("output", "dimensionless")
        # Map output to expected dimension string
        dim_map = {
            "Re": "dimensionless",
            "ΔP": "Pa",
            "P2": "Pa"
        }
        expected_dim_str = dim_map.get(expected_dim, expected_dim)
        dimensional_check = self.step5_check_dimensions(eq_formula, expected_dim_str)

        # Step 6: Independent calculation
        # Prepare inputs in SI units
        si_inputs = {}
        for name, data in unit_check.get("si_values", {}).items():
            si_inputs[name] = data["value"]

        # Map known names to calculator expected names
        name_map = {
            "Density": "rho",
            "Velocity": "V",
            "Pipe diameter": "D",
            "Dynamic viscosity": "mu",
            "Kinematic viscosity": "nu",
            "Friction factor": "f",
            "Pipe length": "L",
            "Pressure at point 1": "P1",
            "Diameter at point 1": "D1",
            "Diameter at point 2": "D2",
            "Velocity at point 1": "V1"
        }

        calc_inputs = {}
        for orig_name, value in si_inputs.items():
            mapped = name_map.get(orig_name, orig_name.lower().replace(" ", "_"))
            calc_inputs[mapped] = value

        calculation = self.step6_independent_calculation(problem_type, calc_inputs)

        # Step 7: Reference verification
        ref_check = self.step7_reference_verification(primary_eq.get("name", ""))

        # Step 8: Physical sanity checks
        sanity_check = self.step8_physical_sanity_checks(problem_type, calculation, calc_inputs)

        # Step 9: Compare with reported (if provided)
        comparison = {}
        if reported_value is not None:
            # Extract the computed value based on problem type
            computed_val = None
            if "Reynolds_number" in calculation:
                computed_val = calculation["Reynolds_number"]
            elif "pressure_drop_Pa" in calculation:
                computed_val = calculation["pressure_drop_Pa"]
            elif "pressure_2_Pa" in calculation:
                computed_val = calculation["pressure_2_Pa"]

            if computed_val is not None:
                comparison = self.step9_compare_results(computed_val, reported_value, tolerance)

        # Step 10: Determine verdict
        all_pass = all([
            dimensional_check.get("status") == "PASS",
            unit_check.get("status") == "PASS",
            "error" not in calculation,
            ref_check.get("status") in ("PASS", "WARNING"),
            sanity_check.get("status") == "PASS",
            comparison.get("status", "PASS") == "PASS" if comparison else True
        ])

        if reported_value is not None and not all_pass:
            verdict = "NOT VERIFIED"
        elif reported_value is None and all_pass:
            verdict = "VERIFIED"
        elif "error" in calculation or unit_check.get("status") == "FAIL":
            verdict = "INSUFFICIENT INFORMATION"
        else:
            verdict = "VERIFIED"

        # Confidence
        if verdict == "VERIFIED" and all_pass:
            confidence = "HIGH"
        elif verdict == "VERIFIED":
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # Compile all results
        all_results = {
            "problem_summary": problem_text[:200],
            "equation": primary_eq,
            "assumptions": assumptions,
            "unit_check": unit_check,
            "dimensional_check": dimensional_check,
            "calculation": calculation,
            "reference_check": ref_check,
            "sanity_check": sanity_check,
            "comparison": comparison,
            "verdict": verdict,
            "confidence": confidence
        }

        # Generate report
        report = self.step10_generate_report(problem_text, all_results)
        all_results["report"] = report

        return all_results


def main():
    parser = argparse.ArgumentParser(description="Engineering verification command")
    parser.add_argument("--problem-file", help="Path to problem markdown file")
    parser.add_argument("--reported-value", type=float, help="Reported result to verify against")
    parser.add_argument("--tolerance", type=float, default=0.01, help="Relative tolerance (default: 0.01)")
    parser.add_argument("--output", choices=["json", "markdown", "text"], default="markdown")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    engine = VerificationEngine(verbose=args.verbose)

    result = engine.verify(
        problem_file=args.problem_file,
        reported_value=args.reported_value,
        tolerance=args.tolerance
    )

    if args.output == "json":
        print(json.dumps(result, indent=2))
    elif args.output == "text":
        print(result.get("report", "No report generated"))
    else:
        print(result.get("report", "No report generated"))

    # Exit with appropriate code
    if result.get("verdict") == "VERIFIED":
        sys.exit(0)
    elif result.get("verdict") == "NOT VERIFIED":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()