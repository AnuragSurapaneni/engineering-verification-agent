# Phase 2 Roadmap: Expanding Equation Verification

## Current Baseline

The repository contains a catalog of 100 fluid-dynamics equations in `eq.md`,
36 structured reference categories in `references/fluid_mechanics/references.json`,
18 standalone calculator types in `scripts/calculate.py`, and four end-to-end
verification workflows. These counts describe different levels of support.
An equation in the catalog or reference database is not automatically a
calculator or an end-to-end verified problem type.

The dimensional checker uses explicit variable dimensions and same-dimension
aliases. It reports unknown symbols as errors; it does not infer that a new
equation is valid from a fallback variable or from similarity analysis alone.

## Expansion Principles

- Add a calculator only when its inputs, output, assumptions, and validity range
  are explicit.
- Require an independent source record before an equation is used for
  end-to-end verification.
- Define every variable's dimensions explicitly. Use aliases only when the
  variables have the same physical dimensions.
- Keep numerical calculation, dimensional validation, reference checks, and
  physical sanity checks separate and report the result of each.
- Treat Buckingham π and similarity analysis as tools for proposing and
  checking relationships; they do not replace source validation or test cases.

## Equation Integration Workflow

1. Select an equation and define its intended validity range and assumptions.
2. Add a stable equation/reference ID and reliable source metadata to
   `references/fluid_mechanics/references.json`.
3. Add or review all variable dimensions in `scripts/dimensional_check.py`.
4. Implement a deterministic calculator in `scripts/calculate.py`, including
   validation for missing and invalid inputs.
5. Add the problem definition, canonical input aliases, expected result key,
   unit, and sanity checks to the end-to-end verifier when reference coverage is
   sufficient.
6. Add problem and expected-result cases for verified, incorrect, and
   insufficient-input outcomes.
7. Update the README and skill documentation to describe the implemented
   support.

## Suggested Priorities

| Phase | Category | Candidate equations |
|-------|----------|---------------------|
| 1 | Boundary layer | Skin friction, thickness correlations, log law |
| 2 | Pipe flow | Laminar friction, Colebrook-White, Swamee-Jain |
| 3 | Drag and lift | Drag coefficient, lift coefficient, induced drag |
| 4 | Compressible flow | Speed of sound, isentropic relations, normal shocks |
| 5 | Open channel and turbomachinery | Froude number, critical depth, Euler turbomachine equation |

## Completion Criteria for Each Addition

- The source and equation form are recorded and validated.
- Dimensions are known for every variable; unknowns cannot pass as
  dimensionless.
- The calculator reports clear errors for missing or invalid inputs.
- Verification cases cover successful comparison, a discrepancy, and missing
  information where those outcomes apply.
- Documentation accurately distinguishes catalog, calculator, and end-to-end
  verification support.
