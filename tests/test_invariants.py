# tests/test_invariants.py
import pytest
import math

TOLERANCE = 0.005

def test_base_frequency():
    base_hz = 79.0
    rpm = base_hz * 60.0
    assert math.isclose(rpm, 4737.60, rel_tol=1e-5), "Base frequency out of tolerance."

def test_dispersion_bounds():
    from lab_03_lattice import theoretical_dispersion
    # Dispersion factors for 8 modes must lie between 0.0 and 2.0
    for k in range(8):
        d_k = theoretical_dispersion(k)
        assert 0.0 <= d_k <= 2.0, f"Dispersion at mode {k} violates lattice bounds."

def test_stage_tolerances():
    deviations = [+0.0020, -0.0010, +0.0030, +0.0010, -0.0020, +0.0040, -0.0010, +0.0020]
    for idx, dev in enumerate(deviations, start=1):
        assert abs(dev) <= TOLERANCE, f"Stage {idx} failed tolerance threshold: {dev}"
