# Darcy-Weisbach Pressure Drop Calculation

## Problem Statement

Water flows through a horizontal circular pipe.

**Given Conditions:**
- Fluid: Water at 300 K
- Density (ρ): 997 kg/m³
- Dynamic viscosity (μ): 8.55 × 10⁻⁴ Pa·s
- Velocity (V): 2 m/s
- Pipe diameter (D): 0.05 m
- Pipe length (L): 10 m
- Darcy friction factor (f): 0.02

**Task:** Calculate the pressure drop (ΔP) using the Darcy-Weisbach equation.

## Governing Equation

ΔP = f × (L / D) × (ρ × V² / 2)

Where:
- ΔP = pressure drop (Pa)
- f = Darcy friction factor (dimensionless)
- L = pipe length (m)
- D = pipe diameter (m)
- ρ = fluid density (kg/m³)
- V = flow velocity (m/s)

## Assumptions

- Steady, incompressible flow
- Fully developed flow
- Horizontal pipe (no elevation change)
- Constant friction factor
- Newtonian fluid

## Expected Result Order of Magnitude

For these conditions: ΔP ~ 1000–10000 Pa (1–10 kPa)