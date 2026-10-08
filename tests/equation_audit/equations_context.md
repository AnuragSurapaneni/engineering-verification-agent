# Equation Audit Skill Test Context

Invoke the `equation-audit` skill and audit each numbered equation on its own
form. Preserve the equation as written. For each, assess symbolic form and
dimensional consistency separately, and compare heat-transfer forms with the
local heat-transfer reference. Assume standard SI heat-transfer notation and
the usual textbook definitions. Temperatures are absolute where raised to a
power; temperature differences are in kelvins.

The set includes plane-wall conduction, convection, radiation, heat exchangers,
thermal resistance, and dimensionless heat-transfer quantities. Unless an
equation itself indicates otherwise, assume steady, one-dimensional conduction
through a homogeneous plane wall with constant properties; Newton cooling with
a specified convection coefficient; gray-surface radiation to large
surroundings; and a heat exchanger represented by a consistent overall
coefficient and area basis in ideal parallel or counterflow (so the LMTD
correction factor is 1).

## Equations to audit

1. `Qdot = h*A*(Ts-Tinf)`
2. `Fo = alpha_th*Lc^2/tau`
3. `Rth = Lc/(k_cond*A)`
4. `Qdot = emissivity*sigma*A*(Ts^3-Tsur^3)`
5. `Bi = h*Lc/k_cond`
6. `Qdot = U_overall*A*DTlm`
7. `Qdot = h*(Ts-Tinf)`
8. `Nu_D = h_avg*Lc/k_l`
9. `alpha_th = k_cond*rho_s*cp_s`
10. `Qdot = k_cond*A*(T1-T2)/Lc`
11. `Rth = k_cond*A/Lc`
12. `Qdot = emissivity*sigma*A*(Ts^4-Tsur^4)`
13. `Bi = k_cond/(h*Lc)`
14. `Fo = alpha_th*tau/Lc^2`
15. `Qdot = 2*k_cond*A*(T1-T2)/Lc`
16. `Qdot = k_cond*A*(T1-T2)/Lc^2`
17. `Rth = 1/(h*A)`
18. `Nu_D = h_avg*Lc*k_l`
19. `Qdot = U_overall*A/DTlm`
20. `alpha_th = k_cond/(rho_s*cp_s)`

## Symbol definitions

- `Qdot`: heat-transfer rate, W
- `q`: heat flux, W/m²
- `h`: convection heat-transfer coefficient, W/(m²·K)
- `h_avg`: average convection heat-transfer coefficient, W/(m²·K)
- `U_overall`: overall heat-transfer coefficient, W/(m²·K)
- `A`: heat-transfer area, m²
- `k_cond`, `k_l`: thermal conductivity, W/(m·K)
- `rho_s`: solid density, kg/m³
- `cp_s`: solid specific heat, J/(kg·K)
- `alpha_th`: thermal diffusivity, m²/s
- `emissivity`: gray-surface emissivity (dimensionless, between 0 and 1)
- `sigma`: Stefan-Boltzmann constant, W/(m²·K⁴)
- `Ts`, `Tsur`, `Tinf`, `T1`, `T2`: absolute temperatures, K
- `Lc`: characteristic length or plane-wall thickness, m
- `tau`: elapsed time, s
- `Fo`, `Bi`, `Nu_D`: Fourier, Biot, and diameter-based Nusselt numbers
  (dimensionless)
- `Rth`: thermal resistance, K/W
- `DTlm`: log-mean temperature difference, K
