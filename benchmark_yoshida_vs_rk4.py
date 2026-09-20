#!/usr/bin/env python3
"""
Benchmark: Yoshida 4th-Order (Symplectic) vs. Runge-Kutta 4 (Non-Symplectic)
1D 8-Site Periodic Harmonic Lattice (TMS-SPEC-084)
Outputs: benchmark_comparison.svg
"""

import math

# --- System Constants ---
N_SITES = 8
MASS = 1.0
KAPPA = 100.0
THETA_STAR = -15.000000
OMEGA_0_HZ = 79.0

# --- Yoshida-4 Weights ---
CBRT_2 = 2.0 ** (1.0 / 3.0)
W0 = -CBRT_2 / (2.0 - CBRT_2)
W1 = 1.0 / (2.0 - CBRT_2)
YOSHIDA_WEIGHTS = [W1, W0, W1]


def compute_forces(q: list[float]) -> list[float]:
    forces = [0.0] * N_SITES
    for j in range(N_SITES):
        q_next = q[(j + 1) % N_SITES]
        q_prev = q[(j - 1 + N_SITES) % N_SITES]
        forces[j] = KAPPA * (q_next - 2.0 * q[j] + q_prev)
    return forces


def compute_hamiltonian(q: list[float], p: list[float]) -> float:
    t_kin = sum(0.5 * (pj ** 2) / MASS for pj in p)
    v_pot = sum(0.5 * KAPPA * (q[(j + 1) % N_SITES] - q[j]) ** 2 for j in range(N_SITES))
    return t_kin + v_pot


# --- Integrator Implementations ---
def verlet_substep(q: list[float], p: list[float], h: float) -> tuple[list[float], list[float]]:
    f = compute_forces(q)
    p_half = [p[j] + 0.5 * h * f[j] for j in range(N_SITES)]
    q_next = [q[j] + (h / MASS) * p_half[j] for j in range(N_SITES)]
    f_next = compute_forces(q_next)
    p_next = [p_half[j] + 0.5 * h * f_next[j] for j in range(N_SITES)]
    return q_next, p_next


def step_yoshida4(q: list[float], p: list[float], dt: float) -> tuple[list[float], list[float]]:
    q_curr, p_curr = q, p
    for w in YOSHIDA_WEIGHTS:
        q_curr, p_curr = verlet_substep(q_curr, p_curr, w * dt)
    return q_curr, p_curr


def step_rk4(q: list[float], p: list[float], dt: float) -> tuple[list[float], list[float]]:
    def derivatives(q_in, p_in):
        dq = [pj / MASS for pj in p_in]
        dp = compute_forces(q_in)
        return dq, dp

    # Stage 1
    k1_q, k1_p = derivatives(q, p)

    # Stage 2
    q2 = [q[j] + 0.5 * dt * k1_q[j] for j in range(N_SITES)]
    p2 = [p[j] + 0.5 * dt * k1_p[j] for j in range(N_SITES)]
    k2_q, k2_p = derivatives(q2, p2)

    # Stage 3
    q3 = [q[j] + 0.5 * dt * k2_q[j] for j in range(N_SITES)]
    p3 = [p[j] + 0.5 * dt * k2_p[j] for j in range(N_SITES)]
    k3_q, k3_p = derivatives(q3, p3)

    # Stage 4
    q4 = [q[j] + dt * k3_q[j] for j in range(N_SITES)]
    p4 = [p[j] + dt * k3_p[j] for j in range(N_SITES)]
    k4_q, k4_p = derivatives(q4, p4)

    # Combine stages
    q_next = [q[j] + (dt / 6.0) * (k1_q[j] + 2.0 * k2_q[j] + 2.0 * k3_q[j] + k4_q[j]) for j in range(N_SITES)]
    p_next = [p[j] + (dt / 6.0) * (k1_p[j] + 2.0 * k2_p[j] + 2.0 * k3_p[j] + k4_p[j]) for j in range(N_SITES)]
    return q_next, p_next


# --- Simulation Runner & SVG Plotter ---
def run_benchmark():
    t0 = 1.0 / OMEGA_0_HZ
    dt = t0 / 80.0  # Intentional step size to highlight long-term stability differences
    total_steps = 100000
    sample_stride = 1000

    # Initial condition: displacement around theta*
    q_init = [THETA_STAR + 0.05 * math.cos(2.0 * math.pi * j / N_SITES) for j in range(N_SITES)]
    p_init = [0.0] * N_SITES

    q_y4, p_y4 = list(q_init), list(p_init)
    q_rk4, p_rk4 = list(q_init), list(p_init)

    h0_y4 = compute_hamiltonian(q_y4, p_y4)
    h0_rk4 = compute_hamiltonian(q_rk4, p_rk4)

    y4_errors = []
    rk4_errors = []
    steps_recorded = []

    print(f"Executing {total_steps} steps (stride={sample_stride})...")

    for s in range(total_steps + 1):
        if s % sample_stride == 0:
            h_y4 = compute_hamiltonian(q_y4, p_y4)
            h_rk4 = compute_hamiltonian(q_rk4, p_rk4)
            err_y4 = abs(h_y4 - h0_y4) / h0_y4
            err_rk4 = abs(h_rk4 - h0_rk4) / h0_rk4

            steps_recorded.append(s)
            y4_errors.append(err_y4)
            rk4_errors.append(err_rk4)

        q_y4, p_y4 = step_yoshida4(q_y4, p_y4, dt)
        q_rk4, p_rk4 = step_rk4(q_rk4, p_rk4, dt)

    print(f"Final Relative Error (Yoshida-4) : {y4_errors[-1]:.3e}")
    print(f"Final Relative Error (RK4)       : {rk4_errors[-1]:.3e}")

    generate_svg("benchmark_comparison.svg", steps_recorded, y4_errors, rk4_errors)


def generate_svg(filename, steps, err_y4, err_rk4):
    w, h = 760, 420
    pad_l, pad_r, pad_t, pad_b = 85, 40, 50, 60
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    # Log10 scaling for errors
    log_min = -13.0
    log_max = -1.0

    def to_coords(step, log_val):
        x = pad_l + (step / steps[-1]) * plot_w
        clamped_log = max(log_min, min(log_max, log_val))
        y = h - pad_b - ((clamped_log - log_min) / (log_max - log_min)) * plot_h
        return f"{x:.1f},{y:.1f}"

    pts_y4 = [to_coords(s, math.log10(max(e, 1e-13))) for s, e in zip(steps, err_y4)]
    pts_rk4 = [to_coords(s, math.log10(max(e, 1e-13))) for s, e in zip(steps, err_rk4)]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
  <text x="{w // 2}" y="30" fill="#e6edf3" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">
    Hamiltonian Energy Drift: Symplectic Yoshida-4 vs. Non-Symplectic RK4
  </text>
  
  <!-- Axes -->
  <line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#30363d" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#30363d" stroke-width="1.5"/>
"""
    # Y-axis log grid
    for log_val in range(int(log_min), int(log_max) + 1, 2):
        y_pos = h - pad_b - ((log_val - log_min) / (log_max - log_min)) * plot_h
        svg += f'  <line x1="{pad_l}" y1="{y_pos:.1f}" x2="{w - pad_r}" y2="{y_pos:.1f}" stroke="#21262d" stroke-dasharray="3" stroke-width="1"/>\n'
        svg += f'  <text x="{pad_l - 10}" y="{y_pos + 4:.1f}" fill="#8b949e" font-size="10" font-family="monospace" text-anchor="end">1e{log_val}</text>\n'

    # Curves
    svg += f'  <polyline fill="none" stroke="#f85149" stroke-width="2.5" points="{" ".join(pts_rk4)}"/>\n'
    svg += f'  <polyline fill="none" stroke="#58a6ff" stroke-width="2" points="{" ".join(pts_y4)}"/>\n'

    # Legend
    svg += f"""  <g transform="translate({pad_l + 20}, {pad_t + 10})">
    <rect width="260" height="52" fill="#161b22" stroke="#30363d" rx="4"/>
    <line x1="12" y1="18" x2="35" y2="18" stroke="#f85149" stroke-width="2.5"/>
    <text x="42" y="22" fill="#f85149" font-size="11" font-family="sans-serif">RK4 (Secular Drift Accretion)</text>
    <line x1="12" y1="36" x2="35" y2="36" stroke="#58a6ff" stroke-width="2"/>
    <text x="42" y="40" fill="#58a6ff" font-size="11" font-family="sans-serif">Yoshida-4 (Shadow Bounded)</text>
  </g>
  <text x="{w // 2}" y="{h - 15}" fill="#8b949e" font-size="11" font-family="sans-serif" text-anchor="middle">Integration Steps (N = 100,000)</text>
</svg>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] Generated {filename}")


if __name__ == "__main__":
    run_benchmark()
