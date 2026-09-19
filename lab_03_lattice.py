#!/usr/bin/env python3
"""
PHYS/CS 482 — Lab 03: Symplectic Lattice Simulation
Student Name: [Your Name]
Student ID:   [Your ID]
"""

import math
import numpy as np

# --- System Constants ---
N_SITES = 8
MASS = 1.0          # Normalized particle mass (kg)
KAPPA = 100.0       # Spring constant (N/m)
BASE_FREQ_HZ = 79.0 # Baseline driver frequency
OMEGA_0 = BASE_FREQ_HZ * 60.0  # RPM equivalent: 4737.60

def theoretical_dispersion(k: int, n_total: int = N_SITES) -> float:
    """
    Problem 1: Compute theoretical acoustic dispersion factor.
    d_k = 2 * sin(k * pi / (2 * N))
    """
    return 2.0 * math.sin((k * math.pi) / (2.0 * n_total))

def velocity_verlet_step(q, p, dt, force_func):
    """
    Problem 2: Implement one symplectic Velocity Verlet step.
    Preserves 2-form dq ^ dp.
    """
    f = force_func(q)
    q_next = q + p * dt + 0.5 * f * (dt ** 2)
    f_next = force_func(q_next)
    p_next = p + 0.5 * (f + f_next) * dt
    return q_next, p_next

def run_lab_audit():
    print(f"=== Running Lab 03: Multi-Site Lattice Evaluation ===")
    print(f"Baseline Frequency: {BASE_FREQ_HZ} Hz ({OMEGA_0:.2f} RPM)")
    
    # Measured modal energies across 8 modes
    E_k = [1200.0, 802.20, 593.14, 454.51, 381.46, 351.24, 314.58, 269.84]
    
    print("\nMode | Energy E_k (J) | Theoretical Dispersion Factor")
    print("-" * 52)
    for k in range(N_SITES):
        d_k = theoretical_dispersion(k)
        print(f"  {k}  |    {E_k[k]:8.2f}    |            {d_k:.4f}")
        
    return E_k

if __name__ == "__main__":
    run_lab_audit()
