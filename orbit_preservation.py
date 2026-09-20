#!/usr/bin/env python3
"""
Orbital Phase-Space Preserver via C-Library ctypes Bridge
Integrates 100,000 steps using compiled libyoshida4.so.
Outputs: orbit_portrait.svg
"""

import ctypes
import math
import os
import sys

N_SITES = 8
THETA_STAR = -15.000000
OMEGA_0_HZ = 79.0

# Load shared object
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libyoshida4.so")
if not os.path.exists(lib_path):
    print(f"[ERROR] {lib_path} not found. Run 'make' first.")
    sys.exit(1)

c_lib = ctypes.CDLL(lib_path)

# ctypes signatures
DoubleArray8 = ctypes.c_double * N_SITES

c_lib.c_yoshida4_integrate_chunk.argtypes = [
    DoubleArray8,
    DoubleArray8,
    ctypes.c_double,
    ctypes.c_int,
]
c_lib.c_yoshida4_integrate_chunk.restype = None

c_lib.c_compute_hamiltonian.argtypes = [DoubleArray8, DoubleArray8]
c_lib.c_compute_hamiltonian.restype = ctypes.c_double


def run_orbit_sim():
    dt = (1.0 / OMEGA_0_HZ) / 100.0
    chunk_size = 50
    chunks = 2000  # Total 100,000 integration steps

    # Initial state centered on theta*
    q_init = [THETA_STAR + 0.15 * math.cos(2.0 * math.pi * j / N_SITES) for j in range(N_SITES)]
    p_init = [0.0] * N_SITES

    q_arr = DoubleArray8(*q_init)
    p_arr = DoubleArray8(*p_init)

    h0 = c_lib.c_compute_hamiltonian(q_arr, p_arr)
    print(f"[INIT] H_0 = {h0:.12f} J | Bridge: ctypes -> libyoshida4.so")

    q0_pts = []
    p0_pts = []

    for _ in range(chunks):
        c_lib.c_yoshida4_integrate_chunk(q_arr, p_arr, dt, chunk_size)
        q0_pts.append(q_arr[0])
        p0_pts.append(p_arr[0])

    hf = c_lib.c_compute_hamiltonian(q_arr, p_arr)
    rel_drift = abs(hf - h0) / h0

    print(f"[DONE] H_final = {hf:.12f} J | Relative Error = {rel_drift:.3e}")
    print(f"[ORBIT] q[0] span: [{min(q0_pts):.4f}, {max(q0_pts):.4f}] rad")

    render_phase_portrait("orbit_portrait.svg", q0_pts, p0_pts)


def render_phase_portrait(filename, q_vals, p_vals):
    w, h = 600, 600
    pad = 60

    q_min, q_max = min(q_vals) - 0.02, max(q_vals) + 0.02
    p_min, p_max = min(p_vals) - 0.2, max(p_vals) + 0.2

    def to_svg(q, p):
        x = pad + ((q - q_min) / (q_max - q_min)) * (w - 2 * pad)
        y = h - pad - ((p - p_min) / (p_max - p_min)) * (h - 2 * pad)
        return f"{x:.1f},{y:.1f}"

    pts = [to_svg(q, p) for q, p in zip(q_vals, p_vals)]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
  <text x="{w // 2}" y="32" fill="#e6edf3" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">
    Invariant Phase-Space Orbit Around theta* = -15.000 rad
  </text>
  
  <!-- Grid Axes -->
  <line x1="{pad}" y1="{h // 2}" x2="{w - pad}" y2="{h // 2}" stroke="#30363d" stroke-width="1"/>
  <line x1="{w // 2}" y1="{pad}" x2="{w // 2}" y2="{h - pad}" stroke="#30363d" stroke-width="1"/>

  <!-- Orbit Path -->
  <polygon fill="none" stroke="#58a6ff" stroke-width="1.5" stroke-opacity="0.8" points="{' '.join(pts)}"/>
  
  <!-- Null Point Center Indicator -->
  <circle cx="{w // 2}" cy="{h // 2}" r="3" fill="#f85149"/>
  <text x="{w // 2 + 8}" y="{h // 2 - 8}" fill="#f85149" font-size="10" font-family="monospace">theta*</text>

  <!-- Labels -->
  <text x="{w // 2}" y="{h - 18}" fill="#8b949e" font-size="11" font-family="sans-serif" text-anchor="middle">Displacement q_0 (rad)</text>
  <text x="20" y="{h // 2}" fill="#8b949e" font-size="11" font-family="sans-serif" text-anchor="middle" transform="rotate(-90 20 {h // 2})">Conjugate Momentum p_0</text>
</svg>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] Generated {filename}")


if __name__ == "__main__":
    run_orbit_sim()
