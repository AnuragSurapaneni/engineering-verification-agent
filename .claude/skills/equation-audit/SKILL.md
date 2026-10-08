---
name: equation-audit
description: Review equations in the current conversation or supplied engineering material for form, dimensional consistency, and reference agreement, then report verdicts with confidence in a table.
metadata:
  version: "1.0.0"
  author: "Engineering Verification Agent"
  tags: "equations, audit, engineering, dimensional-analysis"
---

# Equation Audit Skill

Review explicit equations present in the current conversation or in material the
user asks you to inspect. Extract the equations, assess their form, and summarize
each result in a table with a confidence level.

## Scope

- Include equations from the current user request, relevant conversation turns,
  and files the user explicitly provides or asks you to inspect.
- Preserve each equation as written. Normalize notation only when needed for a
  check, and show the normalized form when it helps explain a finding.
- Do not invent equations or treat every equation in unrelated background as in
  scope. If no explicit equation is present, say so and ask for the material to
  review.
- Check symbolic correctness and dimensional consistency separately from any
  numerical calculation. Do not imply that dimensional consistency alone proves
  an equation correct.

## Review Procedure

1. **Extract and identify.** Number each distinct equation, including relevant
   chained equalities. Record the surrounding claim, definitions, units, and
   assumptions that affect its meaning.
2. **Check dimensions where possible.** From the repository root, use
   `scripts/dimensional_check.py` when the equation can be expressed with its
   supported variables and functions. Choose the expected dimension from the
   described physical quantity. For example:

   ```bash
   python scripts/dimensional_check.py \
     --equation "Re = rho*V*D/mu" --expected dimensionless
   python scripts/dimensional_check.py \
     --equation "dP = f*(L/D)*(rho*V^2/2)" --expected Pa
   ```

   A parser error or unsupported variable means the dimensional check is
   unavailable; it does not by itself mean the equation is wrong. Distinguish a
   genuine mismatch between equation sides from a limitation of the checker.
3. **Check the equation form.** Select the reference catalog that matches the
   equation's domain: use `references/fluid_mechanics/references.json` for fluid
   mechanics and `references/heat_transfer/references.json` for heat transfer.
   For coupled or ambiguous topics, check both when relevant. Compare alternate
   forms, definitions, sign conventions, coefficients, and assumptions. Cite
   the reference entry/source used; a match supports the equation only within
   its stated scope. Catalog inclusion alone is not proof of correctness.
4. **Check the reasoning.** When no direct reference match exists, verify
   algebraic steps from the stated governing equation where possible. Use
   limiting cases or a simple substitution only when they are meaningful.
   Identify missing definitions or assumptions instead of silently filling
   them in.
5. **Assign a verdict and confidence.** Use `Correct` only when the form is
   supported and the stated assumptions fit; use `Incorrect` when a specific
   mathematical, dimensional, or reference contradiction is identified; use
   `Uncertain` when symbols, assumptions, sources, or scope are insufficient.
   State what evidence supports each verdict.

## Confidence

- **HIGH**: The equation agrees with an applicable authoritative reference or
  a clear derivation, dimensional checks pass where applicable, and the required
  assumptions are stated and satisfied.
- **MEDIUM**: The equation is supported by a sound derivation or partial
  reference evidence, but a non-critical assumption or independent check is
  missing.
- **LOW**: Important symbols, units, assumptions, derivation steps, or
  applicable references are missing, or the available checker cannot parse the
  equation.

For an identified contradiction, report the confidence in that finding using
the same scale. Do not lower or raise confidence merely to express how severe an
error is.

## Output

Return one row per distinct equation in this format:

| # | Equation | Verdict | Finding or correction | Confidence |
|---|---|---|---|---|
| 1 | Original equation | Correct / Incorrect / Uncertain | Brief evidence; corrected form if needed | HIGH / MEDIUM / LOW |

After the table, give a short overall summary. Name the local reference or
dimensional check used when relevant. If a numerical result is also present,
only validate it when the context supplies enough values and units; separate
that result from the symbolic equation verdict.

## Benchmark

When changing this skill or its dimensional checker, run the equation-audit
benchmark from the repository root:

```bash
python tests/equation_audit/run_benchmark.py --check-dimensions
```

To score an audit, save its verdicts as JSON with a `results` array of
`{"id": "HT-01", "verdict": "Correct"}` records, then pass the file with
`--results`. The benchmark covers fluid mechanics and heat transfer, including
ambiguous and parser-limited cases. Its expected labels are a reference-aligned
internal baseline; they have not had independent expert review. Do not present
benchmark performance as expert validation.
