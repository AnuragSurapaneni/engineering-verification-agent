# Engineering Verification Skill

This skill describes a verification workflow for engineering calculations. In
this repository, the Python tools and reference data are shared from the root;
the skill scripts orchestrate those canonical tools rather than copying them.

## Supported End-to-End Problems

- Reynolds number
- Darcy-Weisbach pressure drop
- Bernoulli pressure and velocity change in a horizontal pipe
- Mach number

The root calculator CLI has 18 standalone calculation types. A calculation
type is not end-to-end verified until it also has a problem definition, a
reference entry, required-input mapping, and verification cases. `eq.md` is a
catalog and roadmap, not a statement that every listed equation is implemented.

The verifier requires a reported result to return `VERIFIED`. If the result is
absent, or required inputs, units, or a reference are unavailable, it returns
`INSUFFICIENT INFORMATION` and reports any calculation it could complete.

## Run the Verifier

From the repository root:

```bash
python .claude/skills/engineering-verification/scripts/verify.py \
  --problem-file tests/verification_cases/reynolds/reynolds_001/problem.md
```

Options:

```text
--problem-file FILE    Problem Markdown file
--reported-value VAL   Override the reported result; value must be SI
--tolerance FLOAT      Relative comparison tolerance (default: 0.01)
--output FORMAT        json, markdown, or text
--verbose              Show invoked commands
```

The report recognizes reported values in the problem file, including Pa/kPa
pressure results. A `--reported-value` override is interpreted in SI units.

## Tools

| Path | Purpose |
|------|---------|
| `scripts/units.py` | Unit conversion and SI conversion using Pint |
| `scripts/dimensional_check.py` | Dimensional consistency checks; unknown variables fail explicitly |
| `scripts/calculate.py` | 18 deterministic standalone calculator types |
| `scripts/compare.py` | Numeric comparison with relative tolerance |
| `.claude/skills/engineering-verification/scripts/verify.py` | Four supported end-to-end workflows |
| `.claude/skills/engineering-verification/scripts/test_runner.py` | Runs the 10 supported verification cases |

Install Pint for unit conversion:

```bash
pip install pint
```

## Verification Cases

The end-to-end cases are stored in the root `tests/verification_cases/`
directory:

- Reynolds number: verified result, discrepancy, and missing input
- Pressure drop: verified result, discrepancy, and missing input
- Bernoulli: verified result, discrepancy, and missing input
- Mach number: one verified result

The drag example is calculator-only because it has no independent reference
entry yet.

Run all supported cases or one case:

```bash
python .claude/skills/engineering-verification/scripts/test_runner.py
python .claude/skills/engineering-verification/scripts/test_runner.py \
  --case reynolds/reynolds_001
python .claude/skills/engineering-verification/scripts/test_runner.py --json
```

Expected verdicts use the same names as verifier output:

- `VERIFIED`
- `NOT VERIFIED`
- `INSUFFICIENT INFORMATION`

## Extending Support

To add an end-to-end equation, define its stable problem ID, equation,
calculator, result key, and required inputs in `verify.py`; add all required
variable dimensions; add a reference entry with source records; and add problem
cases under `tests/verification_cases/`. Update this guide and `SKILL.md` to
match the implemented support.
