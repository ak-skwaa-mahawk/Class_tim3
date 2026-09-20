import math
import numpy as np
import pytest
from src.transducer_daq import (
    MeasurementBudget,
    calculate_empirical_frequency,
    compute_type_b_relative_uncertainty,
    evaluate_empirical_pi_eff,
    extract_interpolated_crossings,
    run_empirical_audit,
)

def test_type_b_uncertainty_budget():
    budget = MeasurementBudget()
    u_b_rel = compute_type_b_relative_uncertainty(budget)
    assert u_b_rel < 5.0e-6

def test_pi_eff_sensitivity_coefficient():
    rpm_nominal = 4737.60
    u_rpm = 0.002000
    _, _, _, u_c_pi = evaluate_empirical_pi_eff(
        rpm_nominal, 0.0, u_rpm, rpm_nominal
    )
    expected_u_pi = (math.pi / rpm_nominal) * u_rpm
    assert math.isclose(u_c_pi, expected_u_pi, rel_tol=1e-4)

def test_snr_gate_rejection_on_insufficient_sample():
    # Only 2 crossing intervals: cannot establish statistical significance
    crossings = np.array([0.0, 0.01266, 0.02533])
    budget = MeasurementBudget(clock_jitter_s=1e-4)  # High jitter
    res = run_empirical_audit(crossings, budget=budget)
    assert res.snr < 2.0
    assert not res.is_statistically_significant

def test_snr_gate_acceptance_on_calibrated_stream():
    fs = 200000.0
    duration = 5.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    # Drifted driver: 4737.608 RPM -> 78.96013333 Hz
    f_drifted = 4737.608 / 60.0

    # Thermally compensated laboratory environment (dT <= 0.02 K -> thermal_ppm <= 2.3e-7)
    budget = MeasurementBudget(
        timebase_rel=1.0e-7,
        encoder_grating_rel=1.0e-7,
        thermal_ppm=2.3e-7,
        clock_jitter_s=1.0e-9,
    )
    signal = np.sin(2.0 * math.pi * f_drifted * t)
    crossings = extract_interpolated_crossings(t, signal)

    res = run_empirical_audit(crossings, rpm_nominal=4737.60, budget=budget)
    assert res.snr >= 2.0, f"Expected SNR >= 2.0, got {res.snr:.2f}"
    assert res.u_c_rpm < 0.004000, f"Expected u_c < 0.004, got {res.u_c_rpm:.6f}"
    assert res.is_statistically_significant
