---
name: engineering-verification
description: "Engineering verification methodology with deterministic Python tools for dimensional analysis, unit conversion, numerical computation, and reference validation."
compatibility: "Requires Python 3 and the pint package."
metadata:
  version: "1.0.0"
  author: "Engineering Verification Agent"
  tags: "engineering, verification, fluid-mechanics, dimensional-analysis"
---

# Engineering Verification Skill

## Overview

This Skill provides a rigorous methodology for verifying engineering calculations. The agent orchestrates a 10-step verification workflow, calling deterministic Python tools for calculations, dimensional analysis, unit conversion, and comparison.

**Key Principle**: Use the LLM for reasoning and orchestration; use deterministic software for calculations and checks.

---

## When to Use This Skill

Use this Skill when you need to:
- Verify an engineering calculation someone has presented
- Check if a reported result is correct
- Validate dimensional consistency of equations
- Cross-check against authoritative references
- Perform physical sanity checks on results

---

## Verification Workflow

### Step 1: Understand Problem
Parse the natural language problem statement. Extract:
- Known quantities (with units)
- Unknown quantities to solve for
- Domain context (fluid mechanics, thermodynamics, etc.)
- Any stated assumptions or constraints

### Step 2: Extract Equations
Identify the governing equation(s) for the problem:
- Reynolds number: `Re = ρ * V * D / μ`
- Darcy-Weisbach: `ΔP = f * (L/D) * (ρ * V² / 2)`
- Bernoulli: `P₁/ρg + V₁²/2g + z₁ = P₂/ρg + V₂²/2g + z₂`

Output: Equation in symbolic form with variable definitions.

### Step 3: Identify Assumptions
List all explicit and implicit assumptions:
- Flow regime (incompressible, steady, fully developed)
- Fluid properties (Newtonian, constant properties)
- Geometry (circular pipe, horizontal, etc.)
- Boundary conditions

### Step 4: Check Units
Verify all input quantities have consistent units using the units abstraction layer (`scripts/units.py`):
- Convert all inputs to a consistent unit system (SI preferred)
- Flag any unit mismatches or missing units

### Step 5: Check Dimensions
Perform dimensional analysis using `scripts/dimensional_check.py`:
- Verify the governing equation is dimensionally consistent
- Confirm the expected output dimensions match the physical quantity
- Report: PASS / FAIL with details

### Step 6: Independent Calculation
Execute numerical calculation using `scripts/calculate.py`:
- Provide all required inputs in SI units
- Compute the result independently of any reported answer
- Return numerical value with units

### Step 7: Reference Verification
Cross-check the equation and assumptions against `references/fluid_mechanics/references.json`:
- Verify equation form matches authoritative sources
- Check assumptions are documented in references
- Report any discrepancies between references

### Step 8: Physical Sanity Checks
Validate the result against physical expectations:
- Magnitude: Is the order of magnitude reasonable?
- Sign: Is the sign physically correct (e.g., pressure drop positive)?
- Limiting cases: Does result approach expected limits?
- Trends: Does increasing velocity increase pressure drop ~V²?

### Step 9: Compare Results
Compare independent calculation with any reported result using `scripts/compare.py`:
- Compute relative difference
- Check against tolerance (default 1%)
- Report: PASS / FAIL with difference

### Step 10: Generate Verification Report
Produce a structured report with:

```
ENGINEERING VERIFICATION REPORT
================================

Problem: [problem description]
Governing Equation: [equation]
Assumptions: [list]

Dimensional Check: PASS/FAIL
Unit Consistency: PASS/FAIL
Independent Calculation: [value with units]
Reference Check: PASS/FAIL/WARNING
Physical Sanity Check: PASS/FAIL
Comparison with Reported: PASS/FAIL (diff: X%)

Overall Verdict: VERIFIED / NOT VERIFIED / INSUFFICIENT INFORMATION
Confidence: HIGH / MEDIUM / LOW
```

---

## Tool Invocation Patterns

The verifier invokes the canonical tools in the repository root `scripts/`
directory. References and verification cases also live at the repository root;
do not create skill-local copies.

```bash
# Unit conversion
python scripts/units.py convert --value 72 --from km/h --to m/s

# Dimensional check
python scripts/dimensional_check.py --equation "rho*V*D/mu" --expected dimensionless

# Numerical calculation
python scripts/calculate.py --problem reynolds_number --inputs '{"rho":1.225,"V":20,"D":0.1,"mu":1.81e-5}'

# Result comparison
python scripts/compare.py --computed 135000 --reported 135000 --tolerance 0.01
```

---

## Verdict Definitions

| Verdict | Meaning |
|---------|---------|
| **VERIFIED** | All checks pass; independent calculation matches reported result within tolerance; high confidence |
| **NOT VERIFIED** | One or more checks fail; calculation discrepancy; or physical sanity check fails |
| **INSUFFICIENT INFORMATION** | Required inputs, reported result, unit conversion, or reference data are unavailable |

---

## Confidence Levels

| Level | Criteria |
|-------|----------|
| **HIGH** | All required checks pass and the reported result is within tolerance |
| **MEDIUM** | Enough information to calculate, but the reported value or a check fails |
| **LOW** | Required inputs, unit conversion, or reference data are unavailable |

---

## End-to-End Supported Problems

### Supported Equations
1. **Reynolds Number**: `Re = ρVD/μ` — determines flow regime
2. **Darcy-Weisbach Pressure Drop**: `ΔP = f(L/D)(ρV²/2)` — pipe friction loss
3. **Bernoulli Equation**: Energy conservation along a streamline
4. **Mach Number**: `M = V/a`

The verifier requires a reported result to return VERIFIED. Without a reported
result it returns INSUFFICIENT INFORMATION and includes the calculation when
inputs are sufficient. Other calculator types are standalone and are not
end-to-end verified yet.

### Reference Sources
Stored in `references/fluid_mechanics/references.json` with structured format.

---

## Verify Command

The Skill provides a `verify` command that can be invoked in two ways:

### From Current Context
When invoked during a conversation, the Skill uses the problem context from the conversation:

```
/skill engineering-verification verify
```

### From Input File
When invoked with a problem file:

```bash
python .claude/skills/engineering-verification/scripts/verify.py \
  --problem-file tests/verification_cases/reynolds/reynolds_001/problem.md
```

### Verify Command Options
```
python .claude/skills/engineering-verification/scripts/verify.py [OPTIONS]

Options:
  --problem-file FILE    Path to problem markdown file
  --reported-value VAL   Reported result in SI units (overrides the file)
  --tolerance FLOAT      Relative tolerance for comparison (default: 0.01)
  --output FORMAT        Output format: json, markdown, text (default: markdown)
  --verbose              Verbose output
```

---

## Example Prompts

### Verify a Reynolds Number Calculation
> "Verify this Reynolds number calculation: Air at 300K, 1 atm, velocity 20 m/s, pipe diameter 0.1 m. The reported result is Re = 127,000 (turbulent)."

### Verify a Pressure Drop Calculation
> "Check this pressure drop: Water at 300K, velocity 2 m/s, pipe diameter 0.05 m, length 10 m, friction factor 0.02. Reported ΔP = 7.98 kPa."

### Verify a Bernoulli Calculation
> "Verify this Bernoulli problem: Water at 300K, V₁=3 m/s, D₁=0.1 m, D₂=0.05 m, P₁=200 kPa. Reported P₂≈132.7 kPa."

---

## Installation

```bash
# Install the runtime dependency from the project root:
pip install pint
```

Then reference in your CLAUDE.md or invoke directly:
```
/skill engineering-verification
```

---

## Testing

Run the test suite to validate the Skill works:

```bash
python .claude/skills/engineering-verification/scripts/test_runner.py
```

This runs the 10 end-to-end cases for supported equations. The drag example is
calculator-only until it has an independent reference entry.
