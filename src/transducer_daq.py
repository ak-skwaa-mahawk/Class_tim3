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
    return math.sqrt(
        budget.timebase_rel**2
        + budget.encoder_grating_rel**2
        + budget.thermal_ppm**2
    )


def extract_interpolated_crossings(t: np.ndarray, signal: np.ndarray) -> np.ndarray:
    """Extract zero crossings with sub-sample linear interpolation to remove grid jitter."""
    idx = np.where((signal[:-1] < 0) & (signal[1:] >= 0))[0]
    if len(idx) == 0:
        return np.array([])
    
    y0 = signal[idx]
    y1 = signal[idx + 1]
    t0 = t[idx]
    t1 = t[idx + 1]
    
    # Sub-sample root interpolation: t_cross = t0 - y0 * (t1 - t0) / (y1 - y0)
    t_cross = t0 - y0 * (t1 - t0) / (y1 - y0)
    return t_cross


def calculate_empirical_frequency(
    timestamps: np.ndarray,
    budget: Optional[MeasurementBudget] = None,
) -> Tuple[float, float, float, float]:
    """
    Computes RPM from interpolated crossing times along with Type A, Type B, and Type C uncertainties.
    timestamps: 1D array of zero-crossing times in seconds.
    """
    if budget is None:
        budget = MeasurementBudget()

    if len(timestamps) < 2:
        return 0.0, 0.0, 0.0, 0.0

    delta_t = np.diff(timestamps)
    n_intervals = len(delta_t)

    mean_period = float(np.mean(delta_t))
    period_std = float(np.std(delta_t, ddof=1)) if n_intervals > 1 else 0.0

    # Type A: Statistical standard error of the mean period + edge jitter
    u_a_period = (period_std / math.sqrt(n_intervals)) + (budget.clock_jitter_s / math.sqrt(n_intervals))

    freq_hz = 1.0 / mean_period
    rpm = freq_hz * 60.0

    u_a_rpm = (60.0 / (mean_period**2)) * u_a_period
    u_b_rel = compute_type_b_relative_uncertainty(budget)
    u_b_rpm = rpm * u_b_rel
    u_c_rpm = math.sqrt(u_a_rpm**2 + u_b_rpm**2)

    return rpm, u_a_rpm, u_b_rpm, u_c_rpm


def evaluate_empirical_pi_eff(
    rpm_meas: float,
    u_a_rpm: float,
    u_b_rpm: float,
    rpm_nominal: float = 4737.60,
) -> Tuple[float, float, float, float]:
    pi_0 = math.pi
    drift_rpm = rpm_meas - rpm_nominal
    denominator = 1.0 + (drift_rpm / rpm_nominal)
    pi_eff = pi_0 / denominator

    c_rpm = abs(-pi_0 / (rpm_nominal * (denominator**2)))
    u_a_pi = c_rpm * u_a_rpm
    u_b_pi = c_rpm * u_b_rpm
    u_c_pi = math.sqrt(u_a_pi**2 + u_b_pi**2)

    return pi_eff, u_a_pi, u_b_pi, u_c_pi


def run_empirical_audit(
    crossing_timestamps: np.ndarray,
    rpm_nominal: float = 4737.60,
    claimed_drift: float = 0.008000,
    budget: Optional[MeasurementBudget] = None,
) -> EmpiricalResult:
    rpm, u_a_rpm, u_b_rpm, u_c_rpm = calculate_empirical_frequency(
        crossing_timestamps, budget
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
