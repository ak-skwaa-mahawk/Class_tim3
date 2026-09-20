#!/usr/bin/env python3
"""
Test Suite: Empirical Transducer Uncertainty & Hypothesis Gates
Enforces SNR >= 2.0 and GUM Type A/B consistency.
"""

import math
import numpy as np
import pytest
from src.transducer_daq import (
    MeasurementBudget,
    calculate_empirical_frequency,
    compute_type_b_relative_uncertainty,
    evaluate_empirical_pi_eff,
    run_empirical_audit,
)


def test_type_b_uncertainty_budget():
    """Verify systematic budget does not exceed physical limits (sub-ppm class)."""
    budget = MeasurementBudget()
    u_b_rel = compute_type_b_relative_uncertainty(budget)
    assert u_b_rel < 5.0e-6, f"Systematic uncertainty budget too loose: {u_b_rel}"


def test_pi_eff_sensitivity_coefficient():
    """Verify sensitivity coefficient d(pi_eff)/d(rpm) matches first-order Taylor derivation."""
    rpm_nominal = 4737.60
    u_rpm = 0.002000
    _, _, _, u_c_pi = evaluate_empirical_pi_eff(
        rpm_nominal, 0.0, u_rpm, rpm_nominal
    )

    # First-order sensitivity: (pi_0 / Omega_0) * u_Omega
    expected_u_pi = (math.pi / rpm_nominal) * u_rpm
    assert math.isclose(u_c_pi, expected_u_pi, rel_tol=1e-4)


def test_snr_gate_rejection_on_insufficient_sample():
    """Short duration (0.05s) cannot integrate out jitter; must fail the SNR gate."""
    fs = 100000.0
    duration = 0.05
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    signal = np.sin(2.0 * math.pi * 79.0 * t)
    crossings = np.where((signal[:-1] < 0) & (signal[1:] >= 0))[0]

    res = run_empirical_audit(t, crossings)
    assert res.snr < 2.0, "Short sample should not pass the SNR gate."
    assert not res.is_statistically_significant


def test_snr_gate_acceptance_on_calibrated_stream():
    """Sufficient duration (5.0s) with low jitter must resolve 0.008 RPM drift with SNR >= 2."""
    fs = 200000.0
    duration = 5.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    f_drifted = 79.00013333  # Exactly +0.008000 RPM

    budget = MeasurementBudget(clock_jitter_s=1.0e-8)
    jittered_t = t + np.random.normal(0, budget.clock_jitter_s, len(t))
    signal = np.sin(2.0 * math.pi * f_drifted * jittered_t)
    crossings = np.where((signal[:-1] < 0) & (signal[1:] >= 0))[0]

    res = run_empirical_audit(t, crossings, budget=budget)
    assert res.snr >= 2.0, f"Expected SNR >= 2.0, got {res.snr:.2f}"
    assert res.u_c_rpm < 0.004000, f"Uncertainty too wide: {res.u_c_rpm}"
    assert res.is_statistically_significant
