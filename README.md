# Engineering Verification Agent

An agentic engineering verification system built with Claude Code that validates engineering calculations through:

- Equation identification
- Dimensional analysis
- Deterministic numerical computation
- Unit checking and conversion
- Reference cross-validation
- Physical sanity checks

## Quick Start

```bash
cd engineering-verification-agent

# Verify a Reynolds number calculation
python scripts/calculate.py --problem reynolds_number --inputs '{"rho":1.177,"V":20,"D":0.1,"mu":1.85e-5}'

# Run the end-to-end verifier on a problem file
python .claude/skills/engineering-verification/scripts/verify.py \
  --problem-file tests/verification_cases/reynolds/reynolds_001/problem.md

# Check dimensional consistency
python scripts/dimensional_check.py --equation "rho*V*D/mu" --expected dimensionless

# Convert units
python scripts/units.py convert --value 72 --from km/h --to m/s

# Compare results
python scripts/compare.py --computed 127243 --reported 127000 --tolerance 0.01
```

## Repository Structure

```
engineering-verification-agent/
├── .claude/
│   └── skills/
│       └── engineering-verification/
│           ├── SKILL.md          # Verification methodology
│           └── scripts/          # Workflow orchestrator and case runner
├── problems/                     # Engineering problems to verify
│   ├── reynolds_number.md
│   ├── pressure_drop.md
│   └── bernoulli.md
├── references/
│   └── fluid_mechanics/
│       └── references.json       # Structured equation and source records
├── scripts/                      # Deterministic Python CLI tools
│   ├── units.py                  # Unit conversion & dimensional analysis
│   ├── dimensional_check.py      # Equation dimensional verification
│   ├── calculate.py              # Numerical computation engine
│   └── compare.py                # Result comparison with tolerance
├── tests/
│   └── verification_cases/       # End-to-end verification cases
│       ├── reynolds/
│       ├── pressure_drop/
│       ├── bernoulli/
│       └── mach_001/
├── CLAUDE.md                     # Project principles
└── README.md
```

## Verification Workflow (10 Steps)

1. **Understand Problem** - Parse natural language, extract knowns/unknowns
2. **Extract Equations** - Identify governing equations
3. **Identify Assumptions** - List explicit/implicit assumptions
4. **Check Units** - Verify unit consistency via `units.py`
5. **Check Dimensions** - Dimensional analysis via `dimensional_check.py`
6. **Independent Calculation** - Numerical computation via `calculate.py`
7. **Reference Verification** - Cross-check against `references.json`
8. **Physical Sanity Checks** - Magnitude, sign, limiting cases, trends
9. **Compare Results** - Computed vs reported via `compare.py`
10. **Generate Report** - Structured verdict with confidence level

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **VERIFIED** | All checks pass; independent calc matches reported result |
| **NOT VERIFIED** | One or more checks fail; discrepancy detected |
| **INSUFFICIENT INFORMATION** | Required inputs, a reported result, unit conversion, or reference data are unavailable |

## Confidence Levels

- **HIGH**: All required checks pass and the reported result is within tolerance
- **MEDIUM**: Enough information to calculate, but the reported value or a check fails
- **LOW**: Required inputs, unit conversion, or reference data are unavailable

## Supported Scope

The standalone calculator CLI exposes 18 calculation types. The end-to-end
verifier currently supports four problem types and requires a reported result
to issue a VERIFIED verdict:

1. **Reynolds Number**: `Re = ρVD/μ` — flow regime determination
2. **Darcy-Weisbach**: `ΔP = f(L/D)(ρV²/2)` — pipe friction loss
3. **Bernoulli**: `P₁/ρ + V₁²/2 + gz₁ = P₂/ρ + V₂²/2 + gz₂` — energy conservation
4. **Mach Number**: `M = V/a` — ratio of flow speed to sound speed

Other calculator types are callable directly, but do not yet have an end-to-end
verification workflow. [eq.md](eq.md) is an equation catalog and expansion
roadmap, not a claim that all listed equations are implemented.

## Dependencies

```bash
pip install pint
```

## Use as a Codex or Claude Code Skill

The verification skill and its helper scripts are included in this repository.
Install `pint` as shown above before asking the skill to run calculations.

### Codex

Codex discovers repository skills in `.agents/skills`. From the repository
root, copy the bundled skill there once:

```bash
mkdir -p .agents/skills
cp -R .claude/skills/engineering-verification .agents/skills/
```

Start Codex from this repository. Invoke the skill with `$engineering-verification`
or choose it from `/skills`, for example:

```text
$engineering-verification Check this Reynolds number calculation: rho=1.177 kg/m^3, V=20 m/s, D=0.1 m, mu=1.85e-5 Pa*s. The reported result is 127000.
```

See the [Codex skills guide](https://developers.openai.com/codex/skills/) for
skill discovery and invocation details.

### Claude Code

The skill is already installed as a project skill at
`.claude/skills/engineering-verification/`. Start Claude Code from the
repository root and invoke it at the prompt with `/engineering-verification`:

```text
/engineering-verification Check this Reynolds number calculation: rho=1.177 kg/m^3, V=20 m/s, D=0.1 m, mu=1.85e-5 Pa*s. The reported result is 127000.
```

Claude Code can also load it automatically for a matching engineering
verification request. See the [Claude Code skills guide](https://code.claude.com/docs/en/skills).

## CLI and Case Runner

```bash
# Dimensional check
python scripts/dimensional_check.py --equation "rho*V*D/mu" --expected dimensionless

# Deterministic calculation
python scripts/calculate.py --problem reynolds_number --inputs '{"rho":1.177,"V":20,"D":0.1,"mu":1.85e-5}'

# Compare a result
python scripts/compare.py --computed 127243 --reported 127000 --tolerance 0.01

# Run the checked-in end-to-end cases
python .claude/skills/engineering-verification/scripts/test_runner.py
```

## Development Phases

- **Current**: Four end-to-end fluid-mechanics workflows; 18 standalone calculator types
- **Phase 2**: Automated evaluation, regression tests, accuracy metrics
- **Phase 3**: Authoritative references expansion, assumption checking
- **Phase 4**: Local MCP server for tool interfaces
- **Phase 5**: 50-100 problem evaluation suite, failure analysis

## Architecture Principle

> **Use the LLM for reasoning and orchestration; use deterministic software for calculations and checks wherever possible.**

The agent (Claude Code + Skill) orchestrates the workflow; Python tools provide deterministic verification layers.
