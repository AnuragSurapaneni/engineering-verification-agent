# Bernoulli Equation Application

## Problem Statement

Water flows through a horizontal pipe that changes diameter. At point 1, the pipe diameter is 0.1 m. At point 2, the pipe diameter is 0.05 m. The pressure at point 1 is 200 kPa (gauge).

**Given Conditions:**
- Fluid: Water at 300 K
- Density (ρ): 997 kg/m³
- Velocity at point 1 (V₁): 3 m/s
- Diameter at point 1 (D₁): 0.1 m
- Diameter at point 2 (D₂): 0.05 m
- Pressure at point 1 (P₁): 200 kPa (gauge)
- Elevation change: z₁ = z₂ = 0 (horizontal pipe)

**Task:** Calculate the pressure at point 2 (P₂) using the Bernoulli equation with continuity.

## Governing Equations

**Continuity:** A₁V₁ = A₂V₂  →  V₂ = V₁ × (D₁/D₂)²

**Bernoulli (horizontal, no losses):**
P₁/ρ + V₁²/2 = P₂/ρ + V₂²/2

Rearranged:
P₂ = P₁ + ½ρ(V₁² - V₂²)

## Assumptions

- Steady, incompressible flow
- Inviscid (no friction losses)
- Horizontal pipe (z₁ = z₂)
- Along a streamline
- Uniform velocity profiles

## Expected Result

- V₂ = 3 × (0.1/0.05)² = 12 m/s
- P₂ = 200,000 + 0.5 × 997 × (3² - 12²) = 200,000 - 67,297.5 = 132,702.5 Pa ≈ 132.7 kPa

Pressure drops as velocity increases (Venturi effect).
