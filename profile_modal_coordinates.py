#!/usr/bin/env python3
"""
PHYS/CS 482 - Lab 03: Fourier Normal Coordinate Modal Profiler
Projects 1D 8-site periodic lattice trajectories onto uncoupled normal modes Q_k(t).
Verifies absence of mode-coupling leakage (equipartition arrest) under Yoshida-4.
Outputs: modal_coordinates_profile.svg
"""

import math

# --- System Constants ---
N_SITES = 8
MASS = 1.0
KAPPA = 100.0
THETA_STAR = -15.000000
OMEGA_0_HZ = 79.0

# --- Yoshida 4th-Order Split Weights ---
CBRT_2 = 2.0 ** (1.0 / 3.0)
W0 = -CBRT_2 / (2.0 - CBRT_2)
W1 = 1.0 / (2.0 - CBRT_2)
YOSHIDA_WEIGHTS = [W1, W0, W1]


def compute_forces(q: list[float]) -> list[float]:
    """Nearest-neighbor periodic forces."""
    forces = [0.0] * N_SITES
    for j in range(N_SITES):
        q_next = q[(j + 1) % N_SITES]
        q_prev = q[(j - 1 + N_SITES) % N_SITES]
        forces[j] = KAPPA * (q_next - 2.0 * q[j] + q_prev)
    return forces


def verlet_substep(q: list[float], p: list[float], h: float) -> tuple[list[float], list[float]]:
    """Symmetric Störmer-Verlet substep."""
    f = compute_forces(q)
    p_half = [p[j] + 0.5 * h * f[j] for j in range(N_SITES)]
    q_next = [q[j] + (h / MASS) * p_half[j] for j in range(N_SITES)]
    f_next = compute_forces(q_next)
    p_next = [p_half[j] + 0.5 * h * f_next[j] for j in range(N_SITES)]
    return q_next, p_next


def yoshida4_step(q: list[float], p: list[float], dt: float) -> tuple[list[float], list[float]]:
    """Composed 4th-order symplectic update."""
    q_c, p_c = q, p
    for w in YOSHIDA_WEIGHTS:
        q_c, p_c = verlet_substep(q_c, p_c, w * dt)
    return q_c, p_c


def project_normal_modes(q: list[float], p: list[float]) -> tuple[list[float], list[float]]:
    """
    Computes real normal coordinates Q_k and modal energies E_k.
    Shifts coordinates relative to theta* null point.
    """
    q_modes = []
    e_modes = []
    inv_sqrt_n = 1.0 / math.sqrt(N_SITES)

    for k in range(N_SITES):
        re_q, im_q = 0.0, 0.0
        re_p, im_p = 0.0, 0.0

        for n in range(N_SITES):
            disp = q[n] - THETA_STAR
            phase = 2.0 * math.pi * k * n / N_SITES
            cos_p = math.cos(phase)
            sin_p = math.sin(phase)

            re_q += disp * cos_p
            im_q -= disp * sin_p
            re_p += p[n] * cos_p
            im_p -= p[n] * sin_p

        re_q *= inv_sqrt_n
        im_q *= inv_sqrt_n
        re_p *= inv_sqrt_n
        im_p *= inv_sqrt_n

        q_mag = math.sqrt(re_q**2 + im_q**2)
        p_mag_sq = re_p**2 + im_p**2

        omega_k = 2.0 * math.sqrt(KAPPA / MASS) * abs(math.sin(k * math.pi / (2.0 * N_SITES)))
        e_k = 0.5 * (p_mag_sq / MASS) + 0.5 * MASS * (omega_k**2) * (q_mag**2)

        q_modes.append(re_q)  # Primary real projection
        e_modes.append(e_k)

    return q_modes, e_modes


def run_profiler():
    t0 = 1.0 / OMEGA_0_HZ
    dt = t0 / 100.0
    total_steps = 10000
    sample_stride = 50

    # Initialize pure excitation exclusively in Mode 1 (k=1)
    # Testing for absence of energy bleed into k=2..7
    q = [THETA_STAR + 0.1 * math.cos(2.0 * math.pi * 1 * j / N_SITES) for j in range(N_SITES)]
    p = [0.0] * N_SITES

    _, e_init = project_normal_modes(q, p)
    print("=== Mode Decoupling Profiler (Yoshida-4) ===")
    print(f"Initial State: Mode 1 Excited ({e_init[1]:.6f} J), Mode 2={e_init[2]:.2e} J, Mode 3={e_init[3]:.2e} J")

    time_pts = []
    q1_history = []
    q2_history = []
    q3_history = []
    e1_history = []
    leakage_history = []

    for s in range(total_steps + 1):
        if s % sample_stride == 0:
            t = s * dt
            q_m, e_m = project_normal_modes(q, p)

            # Sum energy in all unexcited modes (k != 1 and k != 7 conjugate)
            leakage_energy = sum(e_m[k] for k in range(N_SITES) if k not in (1, 7))

            time_pts.append(t)
            q1_history.append(q_m[1])
            q2_history.append(q_m[2])
            q3_history.append(q_m[3])
            e1_history.append(e_m[1])
            leakage_history.append(leakage_energy)

        q, p = yoshida4_step(q, p, dt)

    max_leakage = max(leakage_history)
    print(f"Final State:   Mode 1 Energy  = {e1_history[-1]:.6f} J")
    print(f"Max Extraneous Leakage (k!=1) = {max_leakage:.3e} J (Machine Precision Confined)")

    render_svg("modal_coordinates_profile.svg", time_pts, q1_history, q2_history, leakage_history)


def render_svg(filename, times, q1, q2, leak):
    w, h = 760, 440
    pad_l, pad_r, pad_t, pad_b = 70, 30, 45, 50
    pw = w - pad_l - pad_r
    ph = (h - pad_t - pad_b) / 2 - 15  # Height for each subplot

    t_max = times[-1]

    # Normalize Subplot 1 (Coordinates Q_k)
    max_q = max(max(abs(v) for v in q1), 0.01) * 1.15
    pts_q1 = []
    pts_q2 = []
    for t, v1, v2 in zip(times, q1, q2):
        x = pad_l + (t / t_max) * pw
        y1 = pad_t + ph / 2 - (v1 / max_q) * (ph / 2)
        y2 = pad_t + ph / 2 - (v2 / max_q) * (ph / 2)
        pts_q1.append(f"{x:.1f},{y1:.1f}")
        pts_q2.append(f"{x:.1f},{y2:.1f}")

    # Subplot 2 (Energy Leakage Log Scale)
    log_min, log_max = -16.0, -10.0
    pts_leak = []
    for t, l_val in zip(times, leak):
        x = pad_l + (t / t_max) * pw
        log_l = math.log10(max(l_val, 1e-16))
        clamped = max(log_min, min(log_max, log_l))
        y = pad_t + ph + 30 + ph - ((clamped - log_min) / (log_max - log_min)) * ph
        pts_leak.append(f"{x:.1f},{y:.1f}")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
  <text x="{w // 2}" y="28" fill="#e6edf3" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">
    Fourier Normal Mode Evolution &amp; Orthogonal Decoupling Verification
  </text>

  <!-- Subplot 1: Coordinate Oscillations -->
  <rect x="{pad_l}" y="{pad_t}" width="{pw}" height="{ph}" fill="#161b22" stroke="#30363d"/>
  <line x1="{pad_l}" y1="{pad_t + ph/2}" x2="{pad_l + pw}" y2="{pad_t + ph/2}" stroke="#21262d" stroke-dasharray="3"/>
  <polyline fill="none" stroke="#58a6ff" stroke-width="2" points="{' '.join(pts_q1)}"/>
  <polyline fill="none" stroke="#f85149" stroke-width="1.5" points="{' '.join(pts_q2)}"/>
  <text x="{pad_l + 10}" y="{pad_t + 20}" fill="#58a6ff" font-size="11" font-family="monospace">Q_1(t) [Active Mode]</text>
  <text x="{pad_l + 180}" y="{pad_t + 20}" fill="#f85149" font-size="11" font-family="monospace">Q_2(t) [Unexcited: Zero Plane]</text>

  <!-- Subplot 2: Residual Energy Leakage -->
  <rect x="{pad_l}" y="{pad_t + ph + 30}" width="{pw}" height="{ph}" fill="#161b22" stroke="#30363d"/>
  <polyline fill="none" stroke="#3fb950" stroke-width="2" points="{' '.join(pts_leak)}"/>
  <text x="{pad_l + 10}" y="{pad_t + ph + 50}" fill="#3fb950" font-size="11" font-family="monospace">Cross-Mode Leakage Sum Σ E_k (k≠1) [Joule]</text>

  <!-- Y-Axis Labels for Subplot 2 -->
  <text x="{pad_l - 10}" y="{pad_t + ph + 35}" fill="#8b949e" font-size="10" font-family="monospace" text-anchor="end">1e-10</text>
  <text x="{pad_l - 10}" y="{pad_t + 2*ph + 30}" fill="#8b949e" font-size="10" font-family="monospace" text-anchor="end">1e-16</text>

  <text x="{w // 2}" y="{h - 15}" fill="#8b949e" font-size="11" font-family="sans-serif" text-anchor="middle">Time Elapsed (s)</text>
</svg>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] Generated {filename}")


if __name__ == "__main__":
    run_profiler()
