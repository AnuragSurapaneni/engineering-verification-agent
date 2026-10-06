# Engineering Verification Agent - Fluid Dynamics Equations

A comprehensive list of 100 fundamental fluid dynamics equations organized by category for skill integration and reference.

## Category 1: Conservation Laws (5 equations)

1. **Continuity Equation (Incompressible)**: ∂ρ/∂t + ∇·(ρV) = 0
2. **Conservation of Mass (Integral Form)**: d/dt ∫_CV ρ dV + ∫_CS ρ(V·n) dA = 0
3. **Conservation of Momentum (Cauchy's Equation)**: ρ DV/Dt = ∇·σ + ρg
4. **Conservation of Energy (First Law)**: ρ De/Dt = ∇·(k∇T) + Φ + ρr
5. **Conservation of Angular Momentum**: dH_CV/dt = ∫_CS r × (ρV)(V·n) dA

## Category 2: Inviscid Flow / Ideal Fluid (8 equations)

6. **Euler's Equation**: ρ(∂V/∂t + V·∇V) = -∇p + ρg
7. **Potential Flow Velocity**: V = ∇φ (velocity potential)
8. **Stream Function**: V = (∂ψ/∂y, -∂ψ/∂x) (2D flow)
9. **Circulation**: Γ = ∮_C V·ds
10. **Kelvin's Circulation Theorem**: dΓ/dt = 0 (inviscid, conservative body forces)
11. **Vorticity Transport Equation**: Dω/Dt = (ω·∇)V + ν∇²ω
12. **Irrotational Flow**: ω = ∇ × V = 0
13. **Method of Images** (for potential flow around boundaries)
14. **Superposition Principle** for Linear Flows
15. **Conformal Mapping** (Joukowski transformation)

## Category 3: Bernoulli and Energy (6 equations)

16. **Bernoulli's Equation** (Steady, Inviscid, Incompressible): p/γ + V²/2g + z = constant
17. **Bernoulli's Equation** (Along a Streamline): p₁/γ + V₁²/2g + z₁ = p₂/γ + V₂²/2g + z₂
18. **Bernoulli with Head Loss**: p₁/γ + V₁²/2g + z₁ = p₂/γ + V₂²/2g + z₂ + h_L
19. **Mechanical Energy Equation**: p/ρ + V²/2 + gz = constant (along streamline)
20. **Extended Bernoulli (Unsteady)**: ∂φ/∂t + p/ρ + V²/2 + gz = constant
21. **Bernoulli Equation for Compressible Isentropic Flow**: ∫dp/ρ + V²/2 + gz = constant
22. **Stagnation Properties**: p₀ = p(1 + (γ-1)/2 M²)^(γ/(γ-1)), T₀ = T(1 + (γ-1)/2 M²)

## Category 4: Viscous Flow / Pipe Flow (15 equations)

23. **Darcy-Weisbach Equation**: Δp = f (L/D) (ρV²/2)
24. **Fanning Friction Factor Relation**: τ_w = f_F (ρV²/2)
25. **Fanning to Darcy**: f_D = 4f_F
26. **Hagen-Poiseuille Law (Laminar)**: Q = πΔpr⁴/(8μL)
27. **Laminar Flow Friction Factor**: f_D = 64/Re (circular pipes)
28. **Entrance Length (Laminar)**: L_e ≈ 0.06ReD
29. **Entrance Length (Turbulent)**: L_e ≈ 4.4Re^(1/6)D
30. **Major Loss + Minor Loss**: h_L = h_f + h_m (friction + minor losses)
31. **Minor Loss Equation**: h_K = K(V²/2g) (loss coefficient method)
32. **Flow Regime Transition**: Re_crit ≈ 2300 (pipe flow)
33. **Reynolds Number (Internal)**: Re = ρVD/μ
34. **Hydraulic Diameter**: D_h = 4A_c/P_wetted
35. **Friction Factor from Moody Chart (implicit)**
36. **Colebrook-White Equation**: 1/√f = -2 log₁₀[(ε/D)/3.7 + 6.9/Re]
37. **Swamee-Jain Approximation**: f = 0.25/[-log₁₀(ε/(3.7D) + 5.74/Re^0.9)]^2
38. **Prandtl Mixing Length Theory**: l = κy (log law layer)
39. **Law of the Wall (Logarithmic)**: u⁺ = (1/κ) ln(y⁺) + B, κ ≈ 0.41, B ≈ 5.2

## Category 5: Open Channel Flow (8 equations)

40. **Froude Number**: Fr = V/√(gD) (rectangular) or V/√(gA/T)
41. **Critical Flow Condition**: Fr = 1 (at critical depth)
42. **Specific Energy**: E = y + V²/2g = y + Q²/(2gA²)
43. **Critical Depth (Rectangular)**: y_c = (Q²/g)^(1/3)
44. **Critical Depth (General)**: A³/T = Q²/g (where T is top width)
45. **Hydraulic Jump (Sequent Depths)**: y₂/y₁ = ½(-1 + √(1 + 8Fr₁²))
46. **Manning's Equation**: Q = (1.49/n) A R^(2/3) S^(1/2) (US units, Q in cfs)
47. **Normal Depth (Uniform Flow)**: S₀ = S_f (bed slope = friction slope)
48. **Gradually Varied Flow Equation**: dy/dx = (S₀ - S_f) / (1 - Fr²)

## Category 6: Compressible Flow / Gas Dynamics (12 equations)

49. **Mach Number**: M = V/a (ratio of flow speed to speed of sound)
50. **Speed of Sound**: a = √(γRT)
51. **Isentropic Relations**: p/p₀ = (T/T₀)^(γ/(γ-1)) = (ρ/ρ₀)^γ
52. **Isentropic Area-Mach Relation**: A/A* = (1/M) [(2/(γ+1)) (1 + (γ-1)/2 M²)]^((γ+1)/(2(γ-1)))
53. **Prandtl-Meyer Function**: ν(M) = √((γ+1)/(γ-1)) arctan√((γ-1)/(γ+1)(M²-1)) - arctan√(M²-1)
54. **Normal Shock Relations**: M₂² = [(γ-1)M₁² + 2]/[2γM₁² - (γ-1)]
55. **Normal Shock Pressure Ratio**: p₀₂/p₀₁ = [(γ+1)M₁²]/[(γ-1)M₁² + 2]^(γ/(γ-1))/( (2γM₁² - (γ-1))/(γ+1) )
56. **Normal Shock Density Ratio**: ρ₂/ρ₁ = (γ+1)M₁²/[(γ-1)M₁² + 2]
57. **Normal Shock Temperature Ratio**: T₂/T₁ = [1 + 2γ/(γ+1)(M₁² - 1)]
58. **Prandtl-Meyer Expansion Fan Turning Angle**: θ = ν(M₂) - ν(M₁)
59. **Oblique Shock Angle**: μ = sin⁻¹(1/M) (Mach angle)
60. **Oblique Shock Polar**: θ-β-M relationship: tanθ = 2cotβ (M²sin²β - 1)/(M²(cos2β + γ + 1)/(2γM² sin²β - 1 + γ))
61. **Isentropic Flow through Nozzle**: V = √(2h₀ - 2∫dp/ρ) or V = √(2γRT₀/(γ-1) [1 - (p/p₀)^((γ-1)/γ)])
62. **Critical Flow Area Ratio**: A*/A = (1/M) [(2/(γ+1)) (1 + (γ-1)/2 M²)]^((γ+1)/(2(γ-1)))

## Category 7: Turbomachinery (6 equations)

63. **Euler Turbomachine Equation**: Δh₀ = U₂V_θ2 - U₁V_θ1
64. **Pump Head**: H = Δp/ρg + V²/2g + z (total head)
65. **Pump Efficiency**: η = (ρgQH)/P_input
66. **Specific Speed**: N_s = ωQ^(1/2)/H^(3/4) (dimensionless or with units)
67. **Dimensionless Flow Coefficient**: Φ = Q/(ωD³)
68. **Dimensionless Head Coefficient**: ψ = gH/(ω²D²)

## Category 8: Drag and Lift (10 equations)

69. **Drag Equation**: F_D = ½ρV²AC_D
70. **Lift Equation**: F_L = ½ρV²AC_L
71. **Drag Coefficient**: C_D = F_D/(½ρV²A)
72. **Lift Coefficient**: C_L = F_L/(½ρV²A)
73. **Lift-to-Drag Ratio**: L/D = C_L/C_D
74. **Parasite Drag**: C_D0 (zero-lift drag coefficient)
75. **Induced Drag**: C_Di = C_L²/(πeAR) (lifting line theory)
76. **Span Efficiency Factor**: e (Oswald's factor, ≤ 1)
77. **Aspect Ratio**: AR = b²/S (b = wingspan, S = wing area)
78. **Thin Airfoil Theory**: C_L = 2πα (for small α in radians)
79. **Kutta Condition**: Flow leaves trailing edge smoothly
80. **Kutta-Joukowski Theorem**: L' = ρVΓ (lift per unit span)

## Category 9: Boundary Layer and Turbulence (12 equations)

81. **Boundary Layer Thickness (Laminar)**: δ/x = 5.0/√Re_x
82. **Boundary Layer Thickness (Turbulent)**: δ/x = 0.37/Re_x^(1/5)
83. **Blasius Boundary Layer Solution**: f''' + ff'' = 0 (similarity equation)
84. **Skin Friction Coefficient (Laminar)**: C_f = 0.664/√Re_x
85. **Skin Friction Coefficient (Turbulent)**: C_f = 0.0592/Re_x^(1/5)
86. **Law of the Wall (Log Law)**: u⁺ = (1/κ) ln(y⁺) + B, κ ≈ 0.41, B ≈ 5.2
87. **Law of the Wall (Viscous Sublayer)**: u⁺ = y⁺ (y⁺ < 5)
88. **Van Driest Transformation**: u⁺_VD = (1/κ) ln(1 + κ²y⁺²) - ln(1 + κ²y⁺_w²) + u⁺_w
89. **Turbulent Kinetic Energy Equation**: Dk/Dt = P_b - ε + ∂/∂x_j((ν + ν_t/σ_k)∂k/∂x_j)
90. **Dissipation Rate Equation**: Dε/Dt = C_ε1(P_b - ε)/k + ∂/∂x_j((ν + ν_t/σ_ε)∂ε/∂x_j)
91. **Mixing Length Theory**: l = κy (Prandtl, log layer)
92. **Eddy Viscosity (Boussinesq)**: τ_turb = μ_t(∂u_i/∂x_j + ∂u_j/∂x_i) - 2/3 kδ_ij

## Category 10: Dimensional Analysis and Similarity (8 equations)

93. **Buckingham π Theorem**: n variables → n - k dimensionless π groups
94. **Reynolds Number**: Re = ρVD/μ (inertial/viscous forces)
95. **Mach Number**: M = V/√(γRT) (velocity/speed of sound)
96. **Froude Number**: Fr = V/√(gL) (inertial/gravity forces)
97. **Euler Number**: Eu = Δp/(ρV²) (pressure/inertial forces)
98. **Weber Number**: We = ρV²L/σ (inertial/surface tension forces)
99. **Prandtl Number**: Pr = μc_p/k (momentum/thermal diffusivity)
100. **Schmidt Number**: Sc = ν/D_AB (momentum/mass diffusivity)