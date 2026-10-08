# Expected Result - Pressure Drop 003 (INSUFFICIENT INFORMATION)

## Expected Equation
ΔP = f * (L/D) * (ρ * V² / 2)

## Expected Approximate Result
Cannot compute - missing Darcy friction factor (f)

## Required Checks
- dimensional_consistency: PASS
- property_consistency: FAIL (f missing)
- numerical_calculation: SKIPPED
- physical_sanity: SKIPPED

## Expected Verdict
INSUFFICIENT INFORMATION

## Required Information
- Darcy friction factor (f) - requires either:
  - Laminar flow: f = 64/Re (but Re needs μ which is given)
  - Turbulent flow: Moody chart or Colebrook-White equation (needs roughness)

## Expected Confidence
N/A
