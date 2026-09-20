#!/usr/bin/env python3
"""
PHYS/CS 482 - Hardware Transducer Calibration & Empirical Invariant DAQ
Separates Type A (statistical) and Type B (systematic) measurement uncertainties.
Performs hypothesis screening of empirical pi_eff against Euclidean pi_0.
"""

import json
import math
import os
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class MeasurementBudget:
    timebase_rel: float = 1.0e-7
    encoder_grating_rel: float = 5.0e-7
    thermal_ppm: float = 11.5 * 0.2 * 1e-6  # 11.5 ppm/K * 0.2 K
    clock_jitter_s: float = 2.5e-8


@dataclass(frozen=True)
class EmpiricalResult:
    measured_rpm: float
    u_a_rpm: float
    u_b_rpm: float
    u_c_rpm: float
    pi_eff: float
    u_c_pi_eff: float
    z_score: float
    snr: float
    is_statistically_significant: bool


def compute_type_b_relative_uncertainty(budget: MeasurementBudget) -> float:
    """Quadratic sum of systematic instrumentation error terms."""
    return math.sqrt(
        budget.timebase_rel**2
        + budget.encoder_grating_rel**2
        + budget.thermal_ppm**2
    )


def calculate_empirical_frequency(
    timestamps: np.ndarray,
    pulse_indices: np.ndarray,
    budget: Optional[MeasurementBudget] = None,
) -> Tuple[float, float, float, float]:
    """
    Computes RPM along with separated Type A, Type B, and combined Type C uncertainties.
    Returns: (rpm, u_a_rpm, u_b_rpm, u_c_rpm)
    """
    if budget is None:
        budget = MeasurementBudget()

    pulse_times = timestamps[pulse_indices]
    if len(pulse_times) < 2:
        return 0.0, 0.0, 0.0, 0.0

    delta_t = np.diff(pulse_times)
    n_intervals = len(delta_t)

    mean_period = float(np.mean(delta_t))

    # Type A: Sample variance of mean period + timing edge jitter
    period_std = float(np.std(delta_t, ddof=1)) if n_intervals > 1 else 0.0
    u_a_period = (period_std / math.sqrt(n_intervals)) + budget.clock_jitter_s

    freq_hz = 1.0 / mean_period
    rpm = freq_hz * 60.0

    # Propagation: u(RPM) = |d(RPM)/dT| * u(T) = (60 / T^2) * u(T)
    u_a_rpm = (60.0 / (mean_period**2)) * u_a_period

    # Type B: Systematic scaling on the measured RPM
    u_b_rel = compute_type_b_relative_uncertainty(budget)
    u_b_rpm = rpm * u_b_rel

    # Combined Type C uncertainty
    u_c_rpm = math.sqrt(u_a_rpm**2 + u_b_rpm**2)

    return rpm, u_a_rpm, u_b_rpm, u_c_rpm


def evaluate_empirical_pi_eff(
    rpm_meas: float,
    u_a_rpm: float,
    u_b_rpm: float,
    rpm_nominal: float = 4737.60,
) -> Tuple[float, float, float, float]:
    """
    Propagates frequency uncertainty into effective pi.
    Returns: (pi_eff, u_a_pi, u_b_pi, u_c_pi)
    """
    pi_0 = math.pi
    drift_rpm = rpm_meas - rpm_nominal

    denominator = 1.0 + (drift_rpm / rpm_nominal)
    pi_eff = pi_0 / denominator

    # Sensitivity coefficient c_rpm = d(pi_eff) / d(rpm_meas)
    c_rpm = abs(-pi_0 / (rpm_nominal * (denominator**2)))

    u_a_pi = c_rpm * u_a_rpm
    u_b_pi = c_rpm * u_b_rpm
    u_c_pi = math.sqrt(u_a_pi**2 + u_b_pi**2)

    return pi_eff, u_a_pi, u_b_pi, u_c_pi


def run_empirical_audit(
    timestamps: np.ndarray,
    pulse_indices: np.ndarray,
    rpm_nominal: float = 4737.60,
    claimed_drift: float = 0.008000,
    budget: Optional[MeasurementBudget] = None,
) -> EmpiricalResult:
    """
    Executes the formal hypothesis gate:
    1. Checks if instrumentation SNR >= 2.0 against claimed drift.
    2. Computes z-score against Euclidean pi_0.
    """
    rpm, u_a_rpm, u_b_rpm, u_c_rpm = calculate_empirical_frequency(
        timestamps, pulse_indices, budget
    )
    pi_eff, _, _, u_c_pi = evaluate_empirical_pi_eff(
        rpm, u_a_rpm, u_b_rpm, rpm_nominal
    )

    snr = claimed_drift / u_c_rpm if u_c_rpm > 0 else 0.0
    z_score = abs(pi_eff - math.pi) / u_c_pi if u_c_pi > 0 else 0.0
    is_significant = (z_score >= 2.0) and (snr >= 2.0)

    return EmpiricalResult(
        measured_rpm=rpm,
        u_a_rpm=u_a_rpm,
        u_b_rpm=u_b_rpm,
        u_c_rpm=u_c_rpm,
        pi_eff=pi_eff,
        u_c_pi_eff=u_c_pi,
        z_score=z_score,
        snr=snr,
        is_statistically_significant=is_significant,
    )


if __name__ == "__main__":
    schema_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "hardware_telemetry_schema.json",
    )
    budget = MeasurementBudget()
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f).get("uncertainty_budget", {})
            budget = MeasurementBudget(
                timebase_rel=data.get("timebase_relative_accuracy", 1.0e-7),
                encoder_grating_rel=data.get(
                    "encoder_grating_error_relative", 5.0e-7
                ),
                thermal_ppm=data.get(
                    "thermal_expansion_coeff_ppm_per_k", 11.5
                )
                * data.get("ambient_temp_delta_k", 0.2)
                * 1e-6,
                clock_jitter_s=data.get("clock_edge_jitter_seconds", 2.5e-8),
            )

    # 5-second simulated capture at 200 kHz with 79.000133 Hz carrier (4737.608 RPM)
    fs = 200000.0
    duration = 5.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    f_carrier = 79.00013333

    # Add realistic jitter and noise
    jittered_t = t + np.random.normal(0, budget.clock_jitter_s, len(t))
    signal = np.sin(2.0 * math.pi * f_carrier * jittered_t)
    zero_crossings = np.where(
        (signal[:-1] < 0) & (signal[1:] >= 0)
    )[0]

    res = run_empirical_audit(t, zero_crossings, budget=budget)

    print("=== Empirical Hardware Invariant Audit ===")
    print(f"Measured RPM        : {res.measured_rpm:.6f}")
    print(f"Type A Uncertainty  : ±{res.u_a_rpm:.6f} RPM")
    print(f"Type B Uncertainty  : ±{res.u_b_rpm:.6f} RPM")
    print(f"Combined (u_c)      : ±{res.u_c_rpm:.6f} RPM")
    print(f"Effective Pi        : {res.pi_eff:.7f} ± {res.u_c_pi_eff:.7f} (k=1)")
    print(f"Signal-to-Noise     : {res.snr:.2f} (Required >= 2.0)")
    print(f"Z-score vs Euclidean: {res.z_score:.2f}σ")

    if res.is_statistically_significant:
        print("[VERDICT] Validated: Empirical drift resolved above instrument floor.")
    else:
        print("[VERDICT] Indistinguishable from Euclidean π0 at 95% confidence.")
