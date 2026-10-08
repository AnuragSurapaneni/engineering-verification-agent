# Equation Audit Test Answer Key

This key is separate from `equations_context.md`; do not use it while auditing.

| # | Expected verdict | Rationale |
|---|---|---|
| 1 | Correct | Newton cooling, `Qdot = h*A*(Ts-Tinf)`. |
| 2 | Incorrect | Fourier number is `Fo = alpha_th*tau/Lc^2`; given form has inverse dimensions. |
| 3 | Correct | Plane-wall conduction resistance is `L/(k*A)`. |
| 4 | Incorrect | Gray-surface radiation uses fourth powers of absolute temperatures, not cubes. |
| 5 | Correct | Standard Biot number is `h*Lc/k_cond` for solid conductivity and characteristic length. |
| 6 | Correct | `Qdot = U*A*DTlm` for ideal parallel/counterflow with correction factor 1. |
| 7 | Incorrect | Newton cooling heat rate also requires area; as written the right side is heat flux. |
| 8 | Correct | Nusselt number is `h_avg*Lc/k_l` using the fluid conductivity. |
| 9 | Incorrect | Thermal diffusivity is `k_cond/(rho_s*cp_s)`, not the product. |
| 10 | Correct | Plane-wall steady conduction heat rate. |
| 11 | Incorrect | The expression is the reciprocal of plane-wall thermal resistance. |
| 12 | Correct | Stefan-Boltzmann net exchange for the stated gray surface and large surroundings. |
| 13 | Incorrect | The expression is the reciprocal of the standard Biot number. |
| 14 | Correct | Fourier number definition. |
| 15 | Incorrect | The standard single-wall equation has no factor of 2; no parallel heat path is stated. |
| 16 | Incorrect | Plane-wall thickness appears to the first power in the denominator. |
| 17 | Correct | Convection resistance is `1/(h*A)`. |
| 18 | Incorrect | Nusselt number divides by fluid conductivity; multiplication is incorrect. |
| 19 | Incorrect | LMTD multiplies `U*A`; dividing by it gives wrong dimensions. |
| 20 | Correct | Thermal diffusivity definition. |

