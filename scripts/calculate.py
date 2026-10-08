#!/usr/bin/env python3
"""
Numerical calculation engine for engineering verification.

Computes independent numerical results for standard engineering equations.
"""

import sys
import json
import argparse
import math
from typing import Dict, Any


def calculate_reynolds(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Reynolds number: Re = rho * V * D / mu"""
    if "nu" in inputs:
        Re = inputs["V"] * inputs["D"] / inputs["nu"]
    else:
        Re = inputs["rho"] * inputs["V"] * inputs["D"] / inputs["mu"]

    if Re < 2300:
        regime = "laminar"
    elif Re <= 4000:
        regime = "transitional"
    else:
        regime = "turbulent"

    return {
        "Reynolds_number": Re,
        "flow_regime": regime,
        "equation": "Re = rho*V*D/mu"
    }


def calculate_pressure_drop(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Darcy-Weisbach pressure drop: dP = f * (L/D) * (rho * V^2 / 2)"""
    f = inputs["f"]
    L = inputs["L"]
    D = inputs["D"]
    rho = inputs["rho"]
    V = inputs["V"]

    dP = f * (L / D) * (rho * V**2 / 2)

    return {
        "pressure_drop_Pa": dP,
        "pressure_drop_kPa": dP / 1000,
        "equation": "ΔP = f * (L/D) * (ρ * V² / 2)"
    }


def calculate_bernoulli(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Bernoulli: P2 = P1 + 0.5*rho*(V1^2 - V2^2) with continuity V2 = V1*(D1/D2)^2"""
    rho = inputs["rho"]
    V1 = inputs["V1"]
    D1 = inputs["D1"]
    D2 = inputs["D2"]
    P1 = inputs["P1"]

    # Continuity
    V2 = V1 * (D1 / D2)**2

    # Bernoulli (horizontal, no losses)
    P2 = P1 + 0.5 * rho * (V1**2 - V2**2)

    return {
        "velocity_2_m_s": V2,
        "pressure_2_Pa": P2,
        "pressure_2_kPa": P2 / 1000,
        "equation": "P2 = P1 + 0.5*rho*(V1^2 - V2^2), V2 = V1*(D1/D2)^2"
    }


def calculate_mach_number(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Mach Number: M = V / a"""
    V = inputs["V"]
    a = inputs["a"]

    M = V / a

    return {
        "mach_number": M,
        "equation": "M = V / a"
    }


def calculate_froude_number(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Froude Number: Fr = V / sqrt(g*D)"""
    V = inputs["V"]
    g = inputs["g"]
    D = inputs["D"]

    Fr = V / math.sqrt(g * D)

    return {
        "froude_number": Fr,
        "equation": "Fr = V / sqrt(g*D)"
    }


def calculate_euler_number(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Euler Number: Eu = deltaP / (rho * V^2)"""
    deltaP = inputs["deltaP"]
    rho = inputs["rho"]
    V = inputs["V"]

    Eu = deltaP / (rho * V**2)

    return {
        "euler_number": Eu,
        "equation": "Eu = Δp / (ρ * V²)"
    }


def calculate_weber_number(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Weber Number: We = rho * V^2 * L / sigma"""
    rho = inputs["rho"]
    V = inputs["V"]
    L = inputs["L"]
    sigma = inputs["sigma"]

    We = rho * V**2 * L / sigma

    return {
        "weber_number": We,
        "equation": "We = ρ * V² * L / σ"
    }


def calculate_prandtl_number(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Prandtl Number: Pr = mu * cp / k"""
    mu = inputs["mu"]
    cp = inputs["cp"]
    k = inputs["k"]

    Pr = mu * cp / k

    return {
        "prandtl_number": Pr,
        "equation": "Pr = μ * cp / k"
    }


def calculate_schmidt_number(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Schmidt Number: Sc = nu / D_AB"""
    nu = inputs["nu"]
    D_AB = inputs["D_AB"]

    Sc = nu / D_AB

    return {
        "schmidt_number": Sc,
        "equation": "Sc = ν / D_AB"
    }


def calculate_hagen_poiseuille(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Hagen-Poiseuille Law (Laminar): Q = πΔpr^4/(8μL)"""
    deltaP = inputs["deltaP"]
    r = inputs["r"]
    mu = inputs["mu"]
    L = inputs["L"]

    Q = math.pi * deltaP * r**4 / (8 * mu * L)

    return {
        "flow_rate_m3_s": Q,
        "equation": "Q = πΔpr^4/(8μL)"
    }


def calculate_drag(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Drag Equation: F_D = 0.5 * rho * V^2 * A * C_D"""
    rho = inputs["rho"]
    V = inputs["V"]
    A = inputs["A"]
    CD = inputs["CD"]

    FD = 0.5 * rho * V**2 * A * CD

    return {
        "drag_Newton": FD,
        "equation": "F_D = 0.5 * ρ * V² * A * C_D"
    }


def calculate_lift(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Lift Equation: F_L = 0.5 * rho * V^2 * A * C_L"""
    rho = inputs["rho"]
    V = inputs["V"]
    A = inputs["A"]
    CL = inputs["CL"]

    FL = 0.5 * rho * V**2 * A * CL

    return {
        "lift_Newton": FL,
        "equation": "F_L = 0.5 * ρ * V² * A * C_L"
    }


def calculate_lift_to_drag(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Lift-to-Drag Ratio: L/D = C_L / C_D"""
    CL = inputs["CL"]
    CD = inputs["CD"]

    LDR = CL / CD

    return {
        "lift_to_drag_ratio": LDR,
        "equation": "L/D = C_L / C_D"
    }


def calculate_skin_friction_laminar(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Skin Friction Coefficient (Laminar): C_f = 0.664 / sqrt(Re_x)"""
    Re_x = inputs["Re_x"]

    Cf = 0.664 / math.sqrt(Re_x)

    return {
        "skin_friction_coefficient": Cf,
        "equation": "C_f = 0.664 / sqrt(Re_x)"
    }


def calculate_skin_friction_turbulent(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Skin Friction Coefficient (Turbulent): C_f = 0.0592 / Re_x^(1/5)"""
    Re_x = inputs["Re_x"]

    Cf = 0.0592 / Re_x**(1/5)

    return {
        "skin_friction_coefficient": Cf,
        "equation": "C_f = 0.0592 / Re_x^(1/5)"
    }


def calculate_boundary_layer_laminar(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Boundary Layer Thickness (Laminar): delta/x = 5.0 / sqrt(Re_x)"""
    Re_x = inputs["Re_x"]
    x = inputs["x"]

    delta = 5.0 * x / math.sqrt(Re_x)

    return {
        "boundary_layer_thickness_m": delta,
        "equation": "δ/x = 5.0 / sqrt(Re_x)"
    }


def calculate_boundary_layer_turbulent(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Boundary Layer Thickness (Turbulent): delta/x = 0.37 / Re_x^(1/5)"""
    Re_x = inputs["Re_x"]
    x = inputs["x"]

    delta = 0.37 * x / Re_x**(1/5)

    return {
        "boundary_layer_thickness_m": delta,
        "equation": "δ/x = 0.37 / Re_x^(1/5)"
    }


def calculate_stagnation(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Calculate Stagnation Properties: p0 = p*(1 + (γ-1)/2 * M^2)^(γ/(γ-1))"""
    p = inputs["p"]
    M = inputs["M"]
    gamma = inputs.get("gamma", 1.4)

    p0 = p * (1 + (gamma - 1) / 2 * M**2)**(gamma / (gamma - 1))
    T0 = inputs.get("T", 300) * (1 + (gamma - 1) / 2 * M**2)

    return {
        "stagnation_pressure_Pa": p0,
        "stagnation_temperature_K": T0,
        "equation": "p0 = p*(1 + (γ-1)/2 * M^2)^(γ/(γ-1))"
    }


def _validate_heat_inputs(inputs: Dict[str, float], positive: tuple[str, ...]) -> None:
    for name, value in inputs.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    for name in positive:
        if inputs[name] <= 0:
            raise ValueError(f"{name} must be greater than zero")


def calculate_plane_wall_conduction(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Steady one-dimensional heat rate through a plane wall."""
    _validate_heat_inputs(inputs, ("k", "A", "L"))
    if inputs["T_hot"] < 0 or inputs["T_cold"] < 0:
        raise ValueError("absolute temperatures must be non-negative")
    heat_rate = inputs["k"] * inputs["A"] * (inputs["T_hot"] - inputs["T_cold"]) / inputs["L"]
    return {
        "heat_rate_W": heat_rate,
        "heat_rate_kW": heat_rate / 1000,
        "equation": "Qdot = k*A*(T_hot-T_cold)/L",
    }


def calculate_convective_heat_transfer(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Newton's law of cooling for a surface with specified h."""
    _validate_heat_inputs(inputs, ("h_conv", "A"))
    if inputs["Ts"] < 0 or inputs["Tinf"] < 0:
        raise ValueError("absolute temperatures must be non-negative")
    heat_rate = inputs["h_conv"] * inputs["A"] * (inputs["Ts"] - inputs["Tinf"])
    return {
        "heat_rate_W": heat_rate,
        "heat_rate_kW": heat_rate / 1000,
        "equation": "Qdot = h_conv*A*(Ts-Tinf)",
    }


def calculate_radiative_heat_transfer(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Net gray-surface radiation to large isothermal surroundings."""
    _validate_heat_inputs(inputs, ("A", "Ts", "Tsur"))
    emissivity = inputs["emissivity"]
    if not 0 <= emissivity <= 1:
        raise ValueError("emissivity must be between zero and one")
    sigma = 5.670374419e-8  # W/(m^2 K^4), exact SI value to current precision
    heat_rate = emissivity * sigma * inputs["A"] * (inputs["Ts"]**4 - inputs["Tsur"]**4)
    return {
        "heat_rate_W": heat_rate,
        "heat_rate_kW": heat_rate / 1000,
        "equation": "Qdot = emissivity*sigmaSB*A*(Ts^4-Tsur^4)",
    }


def calculate_heat_exchanger_lmtd(inputs: Dict[str, float]) -> Dict[str, Any]:
    """Heat-exchanger rate using a supplied corrected log-mean temperature difference."""
    _validate_heat_inputs(inputs, ("U_overall", "A", "DTlm"))
    heat_rate = inputs["U_overall"] * inputs["A"] * inputs["DTlm"]
    return {
        "heat_rate_W": heat_rate,
        "heat_rate_kW": heat_rate / 1000,
        "equation": "Qdot = U_overall*A*DTlm",
    }


def main():
    parser = argparse.ArgumentParser(description="Engineering calculation engine")
    parser.add_argument("--problem", required=True, choices=sorted({
        "reynolds_number", "pressure_drop", "bernoulli", "mach_number",
        "froude_number", "euler_number", "weber_number", "prandtl_number",
        "schmidt_number", "hagen_poiseuille", "drag", "lift",
        "drag_to_lift", "skin_friction_laminar", "skin_friction_turbulent",
        "boundary_layer_laminar", "boundary_layer_turbulent", "stagnation",
        "plane_wall_conduction", "convective_heat_transfer",
        "radiative_heat_transfer", "heat_exchanger_lmtd"
    }),
        help="Problem type to calculate")
    parser.add_argument("--inputs", required=True, help="JSON string of input parameters")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")

    args = parser.parse_args()

    try:
        inputs = json.loads(args.inputs)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON inputs: {e}", file=sys.stderr)
        sys.exit(1)

    calculator = {
        "reynolds_number": calculate_reynolds,
        "pressure_drop": calculate_pressure_drop,
        "bernoulli": calculate_bernoulli,
        "mach_number": calculate_mach_number,
        "froude_number": calculate_froude_number,
        "euler_number": calculate_euler_number,
        "weber_number": calculate_weber_number,
        "prandtl_number": calculate_prandtl_number,
        "schmidt_number": calculate_schmidt_number,
        "hagen_poiseuille": calculate_hagen_poiseuille,
        "drag": calculate_drag,
        "lift": calculate_lift,
        "drag_to_lift": calculate_lift_to_drag,
        "skin_friction_laminar": calculate_skin_friction_laminar,
        "skin_friction_turbulent": calculate_skin_friction_turbulent,
        "boundary_layer_laminar": calculate_boundary_layer_laminar,
        "boundary_layer_turbulent": calculate_boundary_layer_turbulent,
        "stagnation": calculate_stagnation,
        "plane_wall_conduction": calculate_plane_wall_conduction,
        "convective_heat_transfer": calculate_convective_heat_transfer,
        "radiative_heat_transfer": calculate_radiative_heat_transfer,
        "heat_exchanger_lmtd": calculate_heat_exchanger_lmtd,
    }[args.problem]

    try:
        result = calculator(inputs)
    except KeyError as e:
        print(f"Error: Missing required input: {e}", file=sys.stderr)
        sys.exit(1)
    except ZeroDivisionError as e:
        print(f"Error: Division by zero in calculation: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Calculation failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
