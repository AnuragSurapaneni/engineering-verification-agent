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
│           └── SKILL.md          # Core verification methodology
├── problems/                     # Engineering problems to verify
│   ├── reynolds_number.md
│   ├── pressure_drop.md
│   └── bernoulli.md
├── references/
│   └── fluid_mechanics/
│       └── references.json       # Authoritative equation references
├── scripts/                      # Deterministic Python CLI tools
│   ├── units.py                  # Unit conversion & dimensional analysis
│   ├── dimensional_check.py      # Equation dimensional verification
│   ├── calculate.py              # Numerical computation engine
│   └── compare.py                # Result comparison with tolerance
├── tests/
│   └── verification_cases/       # Test cases (PASS/FAIL/INSUFFICIENT)
│       ├── reynolds/
│       ├── pressure_drop/
│       └── bernoulli/
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
| **INSUFFICIENT INFORMATION** | Missing required inputs prevent verification |

## Confidence Levels

- **HIGH**: All checks pass, multiple references agree, tight tolerance
- **MEDIUM**: Most checks pass, minor reference discrepancies
- **LOW**: Limited references, significant assumptions, borderline sanity

## Supported Equations (Phase 1: Fluid Mechanics)

1. **Reynolds Number**: `Re = ρVD/μ` — flow regime determination
2. **Darcy-Weisbach**: `ΔP = f(L/D)(ρV²/2)` — pipe friction loss
3. **Bernoulli**: `P₁/ρ + V₁²/2 + gz₁ = P₂/ρ + V₂²/2 + gz₂` — energy conservation

## Dependencies

```bash
pip install pint
```

## Running Tests

```bash
# Test dimensional check
python scripts/dimensional_check.py --equation "rho*V*D/mu" --expected dimensionless

# Test calculation
python scripts/calculate.py --problem reynolds_number --inputs '{"rho":1.177,"V":20,"D":0.1,"mu":1.85e-5}'

# Test comparison
python scripts/compare.py --computed 127243 --reported 127000 --tolerance 0.01
```

## Development Phases

- **Phase 1** (Current): Core workflow, Fluid Mechanics, Python CLI tools, basic tests
- **Phase 2**: Automated evaluation, regression tests, accuracy metrics
- **Phase 3**: Authoritative references expansion, assumption checking
- **Phase 4**: Local MCP server for tool interfaces
- **Phase 5**: 50-100 problem evaluation suite, failure analysis

## Architecture Principle

> **Use the LLM for reasoning and orchestration; use deterministic software for calculations and checks wherever possible.**

The agent (Claude Code + Skill) orchestrates the workflow; Python tools provide deterministic verification layers.