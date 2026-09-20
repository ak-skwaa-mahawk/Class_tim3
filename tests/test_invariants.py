import math
import pytest
from run_79hz_production_eval import (
    TARGET_RPM,
    STAGE_COUNT,
    TOLERANCE_LIMIT,
    ToroidalResonatorEvaluator,
    DiscreteRingLattice,
)

def test_base_cadence_conversion():
    # 4737.60 RPM corresponds to 78.96 Hz nominal mechanical drive
    f_0 = TARGET_RPM / 60.0
    assert math.isclose(f_0, 78.96, abs_tol=1e-5)

def test_effective_pi_derivation():
    evaluator = ToroidalResonatorEvaluator(TARGET_RPM, STAGE_COUNT, TOLERANCE_LIMIT)
    delta_omega = 0.008000
    eff_pi = evaluator.compute_effective_pi(delta_omega)
    assert math.isclose(eff_pi, 3.1415873, abs_tol=1e-7)

def test_resonator_null_point():
    evaluator = ToroidalResonatorEvaluator(TARGET_RPM, STAGE_COUNT, TOLERANCE_LIMIT)
    delta_omega = 0.008000
    null_theta = evaluator.locate_null_point(delta_omega, phase_offset=0.12)
    assert math.isclose(null_theta, -15.000000, abs_tol=1e-6)

def test_stage_admission_tolerances():
    evaluator = ToroidalResonatorEvaluator(TARGET_RPM, STAGE_COUNT, TOLERANCE_LIMIT)
    simulated_deviations = [0.002, -0.001, 0.003, 0.001, -0.002, 0.004, -0.001, 0.002]
    accumulated = evaluator.calculate_compound_drift(simulated_deviations)
    # Sum: 0.002 - 0.001 + 0.003 + 0.001 - 0.002 + 0.004 - 0.001 + 0.002 = 0.008000
    assert math.isclose(accumulated, 0.008, abs_tol=1e-6)
    assert evaluator.warden.total_passed == STAGE_COUNT
    assert evaluator.warden.total_failed == 0

def test_lattice_modal_confinement():
    lattice = DiscreteRingLattice(STAGE_COUNT)
    energies = lattice.compute_modal_spectrum(step=79)
    assert len(energies) == STAGE_COUNT
    for e in energies:
        assert e > 0.0
