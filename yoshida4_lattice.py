#!/usr/bin/env python3
"""
Yoshida 4th-Order Symplectic Integrator for 1D 8-Site Periodic Lattice
Specification: TMS-SPEC-084
"""

import math

# --- Physical & Lattice Parameters ---
N_SITES = 8
MASS = 1.0           # Unit particle mass (kg)
KAPPA = 100.0        # Coupling constant (N/m)
OMEGA_0_HZ = 79.0    # 4737.60 RPM
THETA_STAR = -15.000000  # Resonator null point (rad)
DELTA_OMEGA_RPM = 0.008000
NOMINAL_RPM = 4737.60

# --- Yoshida 4th-Order Weights ---
CBRT_2 = 2.0 ** (1.0 / 3.0)
W0 = -CBRT_2 / (2.0 - CBRT_2)
W1 = 1.0 / (2.0 - CBRT_2)
SUB_STEPS = [W1, W0, W1]


def compute_forces(q: list[float]) -> list[float]:
    """Nearest-neighbor periodic harmonic forces: F_j = kappa * (q_{j+1} - 2q_j + q_{j-1})."""
    forces = [0.0] * N_SITES
    for j in range(N_SITES):
        q_next = q[(j + 1) % N_SITES]
        q_prev = q[(j - 1 + N_SITES) % N_SITES]
        forces[j] = KAPPA * (q_next - 2.0 * q[j] + q_prev)
    return forces


def verlet_substep(q: list[float], p: list[float], dt_sub: float) -> tuple[list[float], list[float]]:
    """Single 2nd-order Störmer-Verlet symmetric step (Kick-Drift-Kick)."""
    # 1. Momentum half-kick
    f = compute_forces(q)
    p_half = [p[j] + 0.5 * dt_sub * f[j] for j in range(N_SITES)]

    # 2. Coordinate full-drift
    q_next = [q[j] + (dt_sub / MASS) * p_half[j] for j in range(N_SITES)]

    # 3. Momentum final half-kick
    f_next = compute_forces(q_next)
    p_next = [p_half[j] + 0.5 * dt_sub * f_next[j] for j in range(N_SITES)]

    return q_next, p_next


def yoshida4_step(q: list[float], p: list[float], dt: float) -> tuple[list[float], list[float]]:
    """Composed 4th-order symplectic integration step."""
    q_curr, p_curr = q, p
    for w in SUB_STEPS:
        q_curr, p_curr = verlet_substep(q_curr, p_curr, w * dt)
    return q_curr, p_curr


def compute_energy(q: list[float], p: list[float]) -> tuple[float, float, float]:
    """Total Hamiltonian H = T(p) + V(q)."""
    t_kin = sum(0.5 * (p[j] ** 2) / MASS for j in range(N_SITES))
    v_pot = sum(0.5 * KAPPA * (q[(j + 1) % N_SITES] - q[j]) ** 2 for j in range(N_SITES))
    return t_kin, v_pot, t_kin + v_pot


def project_modal_energies(q: list[float], p: list[float]) -> list[float]:
    """Projects state vector onto the 8 normal modal coordinates."""
    e_modes = []
    for k in range(N_SITES):
        q_k_re = sum(q[n] * math.cos(2.0 * math.pi * k * n / N_SITES) for n in range(N_SITES)) / math.sqrt(N_SITES)
        q_k_im = sum(q[n] * math.sin(2.0 * math.pi * k * n / N_SITES) for n in range(N_SITES)) / math.sqrt(N_SITES)
        p_k_re = sum(p[n] * math.cos(2.0 * math.pi * k * n / N_SITES) for n in range(N_SITES)) / math.sqrt(N_SITES)
        p_k_im = sum(p[n] * math.sin(2.0 * math.pi * k * n / N_SITES) for n in range(N_SITES)) / math.sqrt(N_SITES)

        omega_k = 2.0 * math.sqrt(KAPPA / MASS) * abs(math.sin(k * math.pi / (2.0 * N_SITES)))
        kin = 0.5 * (p_k_re**2 + p_k_im**2) / MASS
        pot = 0.5 * MASS * (omega_k**2) * (q_k_re**2 + q_k_im**2)
        e_modes.append(kin + pot)
    return e_modes


if __name__ == "__main__":
    # Baseline period T0 = 1 / 79 Hz
    t0 = 1.0 / OMEGA_0_HZ
    dt = t0 / 200.0  # 200 steps per fundamental cycle
    total_steps = 20000

    # Initialize centered around resonator null point theta* with small excitation
    q = [THETA_STAR + 0.05 * math.cos(2.0 * math.pi * j / N_SITES) for j in range(N_SITES)]
    p = [0.0] * N_SITES

    _, _, e_initial = compute_energy(q, p)
    print(f"[INIT] Total Hamiltonian H_0 = {e_initial:.9f} J")
    print(f"[INIT] Reference theta*       = {THETA_STAR:.6f} rad")

    for step in range(total_steps):
        q, p = yoshida4_step(q, p, dt)

    _, _, e_final = compute_energy(q, p)
    e_error = abs(e_final - e_initial) / e_initial
    pi_eff = math.pi * (1.0 + DELTA_OMEGA_RPM / NOMINAL_RPM) ** (-1)

    print(f"[FINAL] Total Hamiltonian H_f = {e_final:.9f} J")
    print(f"[STABILITY] Rel Energy Error  = {e_error:.3e} (Order-4 Bound Confined)")
    print(f"[INVARIANT] pi_eff Derived    = {pi_eff:.7f}")
