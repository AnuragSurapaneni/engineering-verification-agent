# Expected Result - Bernoulli 001 (PASS)

## Expected Equation
P₂ = P₁ + 0.5*ρ*(V₁² - V₂²),  V₂ = V₁*(D₁/D₂)²

## Expected Approximate Result
V₂ = 3 * (0.1/0.05)² = 12 m/s
P₂ = 200,000 + 0.5 * 997 * (9 - 144) = 200,000 - 67,297.5 = 132,702.5 Pa ≈ 132.7 kPa

## Required Checks
- dimensional_consistency: PASS
- property_consistency: PASS (water ρ=997 kg/m³)
- numerical_calculation: PASS
- physical_sanity: PASS (pressure drops as velocity increases - Venturi effect)

## Expected Verdict
VERIFIED

## Expected Confidence
HIGH
