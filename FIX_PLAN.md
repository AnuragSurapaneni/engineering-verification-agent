# Fix Plan

## Goal

Make the documented verification workflow runnable from the repository root, ensure its reference data and dimensional checks are trustworthy, and align the examples and documentation with the implemented behavior.

## 1. Choose and standardize the runtime layout

- Treat the repository root `scripts/`, `references/`, and `tests/verification_cases/` as the canonical locations.
- Update the skill orchestrator and test runner to resolve those root paths reliably, including when invoked from another working directory.
- Ensure the skill-local scripts either delegate to the canonical tools or are removed from the documented workflow; avoid maintaining two divergent copies.
- Make tool failures explicit in the report instead of allowing missing tools or data to look like successful checks.

**Done when:** invoking the verifier and test runner from the repository root and from another directory reaches the same tools, references, and cases.

## 2. Repair and validate the reference data

- Fix the malformed structure in `references/fluid_mechanics/references.json` and remove accidental duplicate keys or appended fragments.
- Keep one canonical entry per equation, with consistent fields for equation forms, sources, assumptions, and validity limits.
- Add a lightweight data validation step that parses the JSON and checks the expected top-level shape before the verifier uses it.
- Make reference lookup use stable equation identifiers rather than relying only on display-name substring matching.

**Done when:** the file parses, duplicate equation entries are resolved, and each supported calculation can find its intended reference entry.

## 3. Make verification input mapping deliberate

- Define canonical input names for each calculator and map common labels and symbols to them (for example, `Density`, `Density (ρ)`, and `rho`).
- Parse reported values with units consistently, including pressure values in kPa and Pa, and retain the result key and unit instead of treating every report as a Reynolds number.
- Identify missing required values before calculation and return `INSUFFICIENT INFORMATION` with the missing names.
- Ensure equation detection, calculator selection, dimensional expectations, and sanity checks use the same stable problem identifier.

**Done when:** supported problem formats either produce the correct mapped calculation or a specific missing-input/error result, without silently proceeding with incomplete inputs.

## 4. Harden dimensional analysis

- Consolidate `FALLBACK_VARIABLES` and `VARIABLE_BASE_MAP` into one operative mapping and remove unused entries.
- Distinguish unknown variables from known dimensionless quantities. Unknowns should produce an explicit indeterminate/error result rather than being assumed dimensionless.
- Review variable dimensions and expected-output parsing against every equation advertised as supported.
- Add focused cases for powers, parentheses, alternate equation forms, and unknown symbols.

**Done when:** known supported expressions return correct dimensions, and an unknown symbol cannot produce a false pass.

## 5. Reconcile calculators, cases, and documentation

- Decide which equations are genuinely supported by the verifier, separately from those that only have standalone calculators.
- Update `README.md`, the skill README/SKILL, and `PHASE_2_IMPLEMENTATION.md` to state that scope consistently; keep the 100-equation catalog clearly labeled as a catalog or roadmap until implemented.
- Correct the Bernoulli worked example using its stated inputs and equation; correct the drag expected-result arithmetic.
- Reconcile the documented case count with the actual case tree and standardize verdict names and formatting.

**Done when:** every documented supported workflow has a corresponding working calculator and reference, and examples agree with their stated inputs and expected outputs.

## 6. Make the end-to-end verdict dependable

- Define verdict rules for missing information, calculation failures, failed checks, absent reported results, and comparison failures.
- Prevent a missing comparison or an unavailable reference check from being interpreted as a successful verification unless that behavior is explicitly intended and reported.
- Include each check's details and errors in JSON and human-readable reports.
- Add regression cases for each supported problem type and each verdict path, including malformed input, missing inputs, and incorrect reported values.

**Done when:** each case's actual verdict matches its expected verdict, and reports explain every failed or skipped check.

## Suggested implementation order

1. Standardize runtime paths and error handling.
2. Repair reference data and add structural validation.
3. Fix input normalization and missing-information handling.
4. Harden dimensional parsing and variable dimensions.
5. Correct sample calculations and align documentation with the agreed support scope.
6. Add or update regression cases, then run the full verification suite and review its reports.

## Completion criteria

- The verifier and case runner work from supported invocation locations.
- The reference database loads and resolves supported equations.
- Dimensional checks reject unknown-variable ambiguity.
- Sample calculations, expected results, and docs agree.
- Regression cases cover all advertised supported equations and verdict outcomes, with no unexplained failures.
