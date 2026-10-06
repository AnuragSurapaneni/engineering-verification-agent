# Phase 2 Implementation: Testing Equations via Dimensional & Similarity Analysis

## Overview

This phase focuses on testing equations **not** currently in the database using dimensional analysis and similarity principles with the equations that **are** present. The goal is to expand coverage to all 100+ fluid dynamics equations from eq.md.

---

## Core Concepts

### Dimensional Analysis with FALLBACK_VARIABLES

When a variable is not in `VARIABLE_DIMENSIONS`, the `FALLBACK_VARIABLES` mechanism infers dimensions from related variables:

```python
FALLBACK_VARIABLES = {
    "mu_t": "mu",        # turbulent viscosity -> dynamic viscosity
    "epsilon_turb": "epsilon",  # turbulence dissipation -> epsilon
    "C_D_0": "C_D",      # drag coefficient -> reference drag coefficient
    "CL_max": "C_L",     # max lift coefficient -> lift coefficient
}
```

Modified `parse_primary` in `dimensional_check.py` uses fallback when variable not found.

### Similarity Analysis

Use present equation dimension patterns to form new dimensionless groups:

- **Reynolds number** (Re = ρVL/μ) → pipe flow, boundary layers
- **Mach number** (M = V/a) → compressible flow
- **Froude number** (Fr = V/√(gL)) → free surface flows
- **Euler number** (Eu = Δp/ρV²) → pressure-driven flows
- **Weber number** (We = ρV²L/σ) → surface tension effects
- **Prandtl number** (Pr = μc_p/k) → heat transfer
- **Schmidt number** (Sc = μ/ρD) → mass transfer

### Workflow for New Equation Integration

1. **Verify** - Check dimensional consistency with fallback variables
2. **Test** - Create problem.md + expected.md test cases
3. **Add to references** - Expand references.json with equation category
4. **Add calculator** - Implement calculate_* function in scripts/calculate.py
5. **Create test cases** - Add verification test directory

### Prioritization for Expansion (10-week plan)

| Week | Category | Key Equations |
|------|----------|---------------|
| 1-2 | Boundary Layer | Blasius, skin friction, displacement thickness |
| 3-4 | Turbomachinery | Euler turbomachine equation, power, efficiency |
| 5-6 | Drag/Lift Coefficients | Profile drag, induced drag, lift curve slope |
| 7-8 | Compressible Flow | Fanno flow, Rayleigh flow, normal shocks |
| 9-10 | Pipe & Open Channel | Hazen-Williams, Manning, water-hammer |

### Mathematical Foundations

- **Buckingham π theorem**: n variables → n-m dimensionless groups
- **Similarity principles**: Geometric, kinematic, dynamic similarity
- **Dimensionless group formation**: π₁ = f(π₂, π₃, ...)
- **Variable substitution**: Replace unknowns with fallback equivalents

### Code Extension Patterns

**Adding a calculator function** (scripts/calculate.py):

```python
def calculate_<name>(**kwargs):
    """Calculate <equation>."""
    # 1. Validate inputs
    # 2. Compute using dimensional analysis
    # 3. Return JSON with result, dimensions, metadata
```

**Adding a variable dimension** (scripts/dimensional_check.py):

```python
VARIABLE_DIMENSIONS["<var>"] = {"M": 1, "T": -1, ...}
FALLBACK_VARIABLES["<var>"] = "<fallback_var>"
```

**Expanding references.json**:

- Add equation category with: equation, alternate_forms, sources, assumptions, validity_range

### Success Criteria & Deliverables

- [ ] All 100 fluid dynamics equations supported in calculate.py (18+ functions)
- [ ] ~40+ variable dimensions in dimensional_check.py with FALLBACK_VARIABLES
- [ ] 30+ equation categories in references.json
- [ ] Verification test cases for all equation categories (problem.md + expected.md)
- [ ] Dimensional analysis workflow documented and functional
- [ ] Similarity analysis across Re, M, Fr, Eu, We, Pr, Sc groups
- [ ] 10-week incremental expansion plan with milestones

---

## Next Steps

1. **Immediate**: Create test cases for 3-5 new equation categories using dimensional analysis with FALLBACK_VARIABLES
2. **Short-term**: Expand references.json with 10 additional equation categories
3. **Medium-term**: Implement calculator functions for remaining equation types
4. **Long-term**: Full 100-equation coverage with test infrastructure