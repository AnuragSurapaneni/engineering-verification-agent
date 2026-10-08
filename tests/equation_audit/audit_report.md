# Equation Audit Skill Test Report

Audited `equations_context.md` by following `.claude/skills/equation-audit/SKILL.md`.
The dimensional checks used `scripts/dimensional_check.py --domain heat_transfer`.
Equation forms were cross-checked against `references/heat_transfer/references.json`
and its linked source metadata. `Pass` means dimensions are consistent; it does
not establish symbolic correctness.

| # | Equation | Verdict | Finding or correction | Dimensions | Confidence |
|---|---|---|---|---|---|
| 1 | `Qdot = h*A*(Ts-Tinf)` | Correct | Matches Newton cooling (`newton_cooling`); assumptions and symbols fit. | Pass | HIGH |
| 2 | `Fo = alpha_th*Lc^2/tau` | Incorrect | The time and length scales are inverted. Use `Fo = alpha_th*tau/Lc^2`. | Fail | HIGH |
| 3 | `Rth = Lc/(k_cond*A)` | Correct | Matches plane-wall conduction resistance (`plane_wall_resistance`). | Pass | HIGH |
| 4 | `Qdot = emissivity*sigma*A*(Ts^3-Tsur^3)` | Incorrect | Net gray-surface radiation uses fourth powers of absolute temperatures. Use `Ts^4-Tsur^4` (`stefan_boltzmann_net_large_surroundings`). | Fail | HIGH |
| 5 | `Bi = h*Lc/k_cond` | Correct | Matches the standard Biot number with solid conductivity (`biot_number`). | Pass | HIGH |
| 6 | `Qdot = U_overall*A*DTlm` | Correct | Matches the LMTD rate equation with correction factor 1 for the stated ideal parallel/counterflow assumption (`lmtd_heat_exchanger`). | Pass | HIGH |
| 7 | `Qdot = h*(Ts-Tinf)` | Incorrect | The right side has heat-flux dimensions; heat rate needs area. Use `Qdot = h*A*(Ts-Tinf)`. | Fail | HIGH |
| 8 | `Nu_D = h_avg*Lc/k_l` | Correct | Matches the Nusselt definition with fluid conductivity (`nusselt_number`). | Pass | HIGH |
| 9 | `alpha_th = k_cond*rho_s*cp_s` | Incorrect | Product dimensions do not match diffusivity. Use `alpha_th = k_cond/(rho_s*cp_s)` (`thermal_diffusivity`). | Fail | HIGH |
| 10 | `Qdot = k_cond*A*(T1-T2)/Lc` | Correct | Matches steady plane-wall conduction (`plane_wall_heat_rate`) under the stated assumptions. | Pass | HIGH |
| 11 | `Rth = k_cond*A/Lc` | Incorrect | This is the reciprocal of plane-wall resistance. Use `Rth = Lc/(k_cond*A)`. | Fail | HIGH |
| 12 | `Qdot = emissivity*sigma*A*(Ts^4-Tsur^4)` | Correct | Matches the gray-surface net-radiation relation for large surroundings (`stefan_boltzmann_net_large_surroundings`). | Pass | HIGH |
| 13 | `Bi = k_cond/(h*Lc)` | Incorrect | Dimensions pass, but this is the reciprocal of the standard Biot number. Use `Bi = h*Lc/k_cond` (`biot_number`). | Pass | HIGH |
| 14 | `Fo = alpha_th*tau/Lc^2` | Correct | Matches the Fourier number definition (`fourier_number`). | Pass | HIGH |
| 15 | `Qdot = 2*k_cond*A*(T1-T2)/Lc` | Incorrect | Dimensions pass, but the factor 2 is unsupported for the stated single wall. Use `Qdot = k_cond*A*(T1-T2)/Lc` (`plane_wall_heat_rate`). | Pass | HIGH |
| 16 | `Qdot = k_cond*A*(T1-T2)/Lc^2` | Incorrect | Wall thickness is to the first power in the denominator. Use `/Lc` (`plane_wall_heat_rate`). | Fail | HIGH |
| 17 | `Rth = 1/(h*A)` | Correct | Matches convection resistance (`convection_resistance`). | Pass | HIGH |
| 18 | `Nu_D = h_avg*Lc*k_l` | Incorrect | Nusselt number divides by fluid conductivity. Use `Nu_D = h_avg*Lc/k_l` (`nusselt_number`). | Fail | HIGH |
| 19 | `Qdot = U_overall*A/DTlm` | Incorrect | The log-mean temperature difference multiplies `U*A`; division has the wrong dimensions. Use `Qdot = U_overall*A*DTlm` (`lmtd_heat_exchanger`). | Fail | HIGH |
| 20 | `alpha_th = k_cond/(rho_s*cp_s)` | Correct | Matches thermal diffusivity (`thermal_diffusivity`). | Pass | HIGH |

## Test outcome

- Equation classifications matched the separate answer key: **20/20**.
- Correct equations recognized: **10/10**.
- Incorrect equations recognized: **10/10**.
- Eight invalid equations failed dimensional analysis. Two incorrect equations
  (#13 and #15) were dimensionally consistent and were rejected by comparison
  with the standard equation form and stated assumptions.
- Reference records cite *A Heat Transfer Textbook*, chapters 2–6 and 10. The
  official text states the conventional Biot and Nusselt definitions and the
  LMTD relation; see [A Heat Transfer Textbook, sixth edition](https://ahtt.mit.edu/wp-content/uploads/2024/04/AHTTv600.pdf).

