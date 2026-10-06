# Engineering Verification Skill v1.0.0

## Overview

This Skill provides a rigorous methodology for verifying engineering calculations. The agent orchestrates a 10-step verification workflow, calling deterministic Python tools for calculations, dimensional analysis, unit conversion, and reference validation.

**Key Principle**: Use the LLM for reasoning and orchestration; use deterministic software for calculations and checks wherever possible.

## Installation

```bash
# In your project root:
mkdir -p .claude/skills
cp -r /path/to/engineering-verification .claude/skills/
pip install pint
```

Then reference in your CLAUDE.md or invoke directly:

```
/skill engineering-verification
```

## Usage

### From Claude Code

The Skill provides a `verify` command with two invocation methods:

#### From Conversation Context

When invoked during a conversation, the Skill uses the problem context:

```
/skill engineering-verification verify
```

#### From a Problem File

```bash
python scripts/verify.py --problem-file examples/reynolds_number.md
python scripts/verify.py --problem-file examples/pressure_drop.md --reported-value 127000
```

### Verify Command Options

```
python scripts/verify.py [OPTIONS]

Options:
  --problem-file FILE    Path to problem markdown file
  --reported-value VAL   Reported result to verify against (optional)
  --tolerance FLOAT      Relative tolerance for comparison (default: 0.01)
  --output FORMAT        Output format: json, markdown, text (default: markdown)
  --verbose              Verbose output
```

### Example Prompts

- "Verify this Reynolds number calculation: Air at 300K, 1 atm, velocity 20 m/s, pipe diameter 0.1 m. The reported result is Re = 127,000 (turbulent)."
- "Check this pressure drop: Water at 300K, velocity 2 m/s, pipe diameter 0.05 m, length 10 m, friction factor 0.02. Reported ΔP = 7.98 kPa."
- "Verify this Bernoulli problem: Water at 300K, V₁=3 m/s, D₁=0.1 m, D₂=0.05 m, P₁=200 kPa. Reported P₂=130.2 kPa."

## Supported Domains (v1)

### Fluid Mechanics

1. **Reynolds Number**: `Re = ρVD/μ` — determines flow regime (laminar if Re < 2300, turbulent if Re > 4000)
2. **Darcy-Weisbach Pressure Drop**: `ΔP = f(L/D)(ρV²/2)` — pipe friction loss
3. **Bernoulli Equation**: Energy conservation along a streamline

## Tooling

The Skill includes the following deterministic Python CLI tools:

| Tool | Purpose |
|------|---------|
| `scripts/units.py` | Unit conversion, dimensional analysis, SI conversion (wraps Pint) |
| `scripts/dimensional_check.py` | Equation dimensional consistency analysis |
| `scripts/calculate.py` | Numerical computation for all 3 fluid mechanics equations |
| `scripts/compare.py` | Compare computed vs reported values with configurable tolerance |
| `scripts/verify.py` | Full 10-step verification workflow |
| `scripts/test_runner.py` | Run all verification test cases |

## Dependencies

- Python 3.8+
- `pip install pint`

## Verification Cases

The Skill includes test cases covering all three verdict types:

| Verdict | Cases |
|---------|-------|
| **VERIFIED** | PASS cases: correct equation + correct calculation |
| **NOT VERIFIED** | FAIL cases: correct equation + wrong numerical result |
| **INSUFFICIENT INFORMATION** | INSUFFICIENT_INFORMATION cases: missing required properties |

Example test case structure:

```
tests/verification_cases/reynolds/reynolds_001/
├── problem.md          # Problem statement
└── expected.md         # Expected verdict and confidence

Problem cases per domain:
- Reynolds: 3 cases (PASS, FAIL, INSUFFICIENT_INFORMATION)
- Pressure drop: 3 cases (PASS, FAIL, INSUFFICIENT_INFORMATION)
- Bernoulli: 3 cases (PASS, FAIL, INSUFFICIENT_INFORMATION)
Total: 9 test cases
```

## Running Tests

```bash
# Run all test cases
python scripts/test_runner.py

# Run specific case
python scripts/test_runner.py --case reynolds/reynolds_001

# Output JSON summary
python scripts/test_runner.py --json
```

## Extending the Skill

### Adding New Domains

1. Add equation definitions to SKILL.md
2. Add calculator functions in `scripts/calculate.py`
3. Add variable dimensions in `scripts/dimensional_check.py`
4. Add references in `references/fluid_mechanics/references.json`
5. Add test cases in `tests/verification_cases/`

### Adding New Equations

Ensure the calculator function returns a dict with:
- `equation`: String describing the equation
- Result-specific keys (e.g., `Reynolds_number`, `pressure_drop_Pa`, `pressure_2_Pa`, `velocity_2_m_s`)

## Skill Structure

```
engineering-verification/
├── SKILL.md              # Main skill definition (YAML frontmatter + methodology)
├── README.md             # Installation & usage instructions
├── scripts/
│   ├── units.py          # Unit conversion & dimensional analysis
│   ├── dimensional_check.py  # Equation dimensional analysis
│   ├── calculate.py      # Numerical computation engine
│   ├── compare.py        # Result comparison with tolerance
│   ├── verify.py         # Full 10-step verification workflow
│   └── test_runner.py    # Test case runner
├── references/
│   └── fluid_mechanics/
│       └── references.json  # Authoritative references
├── examples/
│   ├── reynolds_number.md
│   ├── pressure_drop.md
│   └── bernoulli.md
└── tests/
    └── verification_cases/
        ├── reynolds/
        │   ├── reynolds_001/    # PASS
        │   ├── reynolds_002/    # FAIL
        │   └── reynolds_003/    # INSUFFICIENT_INFORMATION
        ├── pressure_drop/
        │   ├── pressure_drop_001/    # PASS
        │   ├── pressure_drop_002/    # FAIL
        │   └── pressure_drop_003/    # INSUFFICIENT_INFORMATION
        └── bernoulli/
            ├── bernoulli_001/    # PASS
            ├── bernoulli_002/    # FAIL
            └── bernoulli_003/    # INSUFFICIENT_INFORMATION
```

## Skill Version History

- **v1.0.0** (2026-10-06): Initial release with Fluid Mechanics (Reynolds, Darcy-Weisbach, Bernoulli) and 9 test cases
- **v1.1.0** (planned): Heat transfer equations
- **v1.2.0** (planned): Thermodynamics
- **v2.0.0** (planned): Multi-domain support, MCP integration