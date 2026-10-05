# Engineering Verification Skill

## Overview

This skill defines a rigorous procedure for verifying engineering calculations. The agent orchestrates a 10-step verification workflow, calling deterministic Python tools for calculations, dimensional analysis, unit conversion, and comparison.

**Key Principle**: Use the LLM for reasoning and orchestration; use deterministic software for calculations and checks.

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
Verify all input quantities have consistent units using the units abstraction layer (`scripts/units.py`).
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

All tools are invoked via subprocess (CLI):

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
| **INSUFFICIENT INFORMATION** | Missing required inputs, properties, or assumptions prevent verification |

---

## Confidence Levels

| Level | Criteria |
|-------|----------|
| **HIGH** | All checks PASS, multiple references agree, result matches within tight tolerance |
| **MEDIUM** | Most checks PASS, minor reference discrepancies, or wider tolerance needed |
| **LOW** | Limited reference coverage, significant assumptions, or borderline physical sanity |

---

## Domain: Fluid Mechanics (Phase 1)

### Supported Equations
1. **Reynolds Number**: `Re = ρVD/μ` — determines flow regime
2. **Darcy-Weisbach Pressure Drop**: `ΔP = f(L/D)(ρV²/2)` — pipe friction loss
3. **Bernoulli Equation**: Energy conservation along a streamline

### Required Fluid Properties (at given T, P)
- Density (ρ)
- Dynamic viscosity (μ)
- Kinematic viscosity (ν = μ/ρ)

### Reference Sources
Stored in `references/fluid_mechanics/references.json` with structured format.