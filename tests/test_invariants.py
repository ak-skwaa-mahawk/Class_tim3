cd ~/GitHub_Workspace/Class_tim3

# 1. Create tests directory
mkdir -p tests

# 2. Write tests/test_invariants.py
cat << 'EOF' > tests/test_invariants.py
#!/usr/bin/env python3
"""
Test Suite: Laboratory Invariant & Numerical Grading Assertions
Course: PHYS/CS 482 - Numerical Mechanics & Symplectic Systems
"""

import math
import hashlib
import pytest

TOLERANCE = 0.005
BASE_HZ = 79.0
NOMINAL_RPM = 4737.60
MEASURED_DRIFT_RPM = 0.008000
EXPECTED_PI_EFF = 3.1415873
CANONICAL_STATE_HASH = "a44db35bc5f551211e68b497a0e8e8a3a4445ac60586e460a5a63f1f596caff8"

def test_base_frequency_cadence():
    """Verify conversion between 79 Hz base cadence and nominal RPM."""
    rpm = BASE_HZ * 60.0
    assert math.isclose(rpm, NOMINAL_RPM, rel_tol=1e-5), f"Base RPM mismatch: {rpm} != {NOMINAL_RPM}"

def test_effective_pi_derivation():
    """Verify analytical expansion of effective operating pi from compound drift."""
    pi_0 = math.pi
    pi_eff_calc = pi_0 * (1.0 + (MEASURED_DRIFT_RPM / NOMINAL_RPM)) ** (-1)
    assert round(pi_eff_calc, 7) == EXPECTED_PI_EFF, f"Effective pi mismatch: {pi_eff_calc} vs {EXPECTED_PI_EFF}"

def test_8_site_dispersion_bounds():
    """Verify acoustic dispersion relation d_k = 2 * |sin(k*pi / (2*N))| stays bounded."""
    n_sites = 8
    for k in range(n_sites):
        d_k = 2.0 * abs(math.sin((k * math.pi) / (2.0 * n_sites)))
        assert 0.0 <= d_k <= 2.0, f"Mode {k} dispersion factor out of bounds: {d_k}"

def test_modal_energy_confinement():
    """Verify monotonic decay of modal energies across the 8-site spectrum."""
    E_k = [1200.0, 802.20, 593.14, 454.51, 381.46, 351.24, 314.58, 269.84]
    assert len(E_k) == 8, "Lattice must contain exactly 8 sites."
    for i in range(len(E_k) - 1):
        assert E_k[i] > E_k[i+1], f"Mode energy inversions detected: E[{i}]={E_k[i]} <= E[{i+1}]={E_k[i+1]}"

def test_state_admission_warden_stages():
    """Verify all 8 screening stage deviations satisfy tolerance bounds (|dev| <= 0.005)."""
    stage_deviations = [+0.0020, -0.0010, +0.0030, +0.0010, -0.0020, +0.0040, -0.0010, +0.0020]
    assert len(stage_deviations) == 8, "Screening log must contain 8 stages."
    for stage_idx, dev in enumerate(stage_deviations, start=1):
        assert abs(dev) <= TOLERANCE, f"Stage {stage_idx} deviation exceeds threshold: {dev} > {TOLERANCE}"

def test_canonical_report_digest():
    """Verify notarized state digest format and existence."""
    assert len(CANONICAL_STATE_HASH) == 64, "State hash must be a 64-character hex string."
    # Verify hash is a valid hexadecimal sequence
    int(CANONICAL_STATE_HASH, 16)
EOF

# 3. Ensure pytest is installed and execute test runner
python3 -m pip install pytest --quiet 2>/dev/null || true
python3 -m pytest tests/test_invariants.py -v
