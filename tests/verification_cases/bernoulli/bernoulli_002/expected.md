# Expected Result - Bernoulli 002 (FAIL)

## Expected Equation
P₂ = P₁ + 0.5*ρ*(V₁² - V₂²),  V₂ = V₁*(D₁/D₂)²

## Expected Approximate Result
V₂ = 12 m/s
P₂ = 132,709 Pa (132.7 kPa)

## Required Checks
- dimensional_consistency: PASS
- property_consistency: PASS
- numerical_calculation: FAIL (reported 200,000 vs computed 132,709, diff = 50.7%)
- physical_sanity: FAIL (reported no pressure drop violates Venturi effect - velocity increases, pressure must drop)

## Expected Verdict
FAIL

## Expected Confidence
HIGH