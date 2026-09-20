// audit_invariants.rs — Independent Symplectic 2-Form Auditor
// Links to libyoshida4.so to evaluate Jacobian: J^T * J_sym * J == J_sym.

use std::os::raw::{c_double, c_int};

const N_SITES: usize = 8;
const DIM: usize = 2 * N_SITES; // 16-dimensional phase space

#[link(name = "yoshida4")]
extern "C" {
    pub fn c_yoshida4_step(q: *mut c_double, p: *mut c_double, dt: c_double);
    pub fn c_yoshida4_integrate_chunk(
        q: *mut c_double,
        p: *mut c_double,
        dt: c_double,
        steps: c_int,
    );
    pub fn c_compute_hamiltonian(q: *const c_double, p: *const c_double) -> c_double;
}

fn integrate_state(state: &[f64; DIM], dt: f64, steps: i32) -> [f64; DIM] {
    let mut q = [0.0; N_SITES];
    let mut p = [0.0; N_SITES];

    for i in 0..N_SITES {
        q[i] = state[i];
        p[i] = state[N_SITES + i];
    }

    unsafe {
        c_yoshida4_integrate_chunk(q.as_mut_ptr(), p.as_mut_ptr(), dt, steps as c_int);
    }

    let mut out = [0.0; DIM];
    for i in 0..N_SITES {
        out[i] = q[i];
        out[N_SITES + i] = p[i];
    }
    out
}

fn compute_energy(state: &[f64; DIM]) -> f64 {
    let mut q = [0.0; N_SITES];
    let mut p = [0.0; N_SITES];
    for i in 0..N_SITES {
        q[i] = state[i];
        p[i] = state[N_SITES + i];
    }
    unsafe { c_compute_hamiltonian(q.as_ptr(), p.as_ptr()) }
}

fn main() {
    println!("========================================================================");
    println!("  RUST SYMPLECTIC 2-FORM AUDITOR — TMS-SPEC-084 / Class_tim3");
    println!("========================================================================");

    let dt = 0.001;
    let steps = 50; // 50 composite steps

    // Initial state centered around resonator null point (-15.0 rad)
    let mut z0 = [0.0; DIM];
    for i in 0..N_SITES {
        let theta = 2.0 * std::f64::consts::PI * (i as f64) / (N_SITES as f64);
        z0[i] = -15.0 + 0.15 * theta.sin();
        z0[N_SITES + i] = 0.10 * theta.cos();
    }

    let h0 = compute_energy(&z0);
    let z_base_final = integrate_state(&z0, dt, steps);
    let h_final = compute_energy(&z_base_final);
    let rel_energy_err = ((h_final - h0) / h0).abs();

    println!("[FFI] Shared Object Loaded   : libyoshida4.so");
    println!("[INTEG] Chunk Step Count     : {} steps (dt = {})", steps, dt);
    println!("[ENERGY] Initial Energy H_0  : {:.12} J", h0);
    println!("[ENERGY] Final Energy H_t    : {:.12} J", h_final);
    println!("[ENERGY] Relative Drift      : {:.3e}", rel_energy_err);

    // Compute numerical Jacobian J = d(z_final)/d(z_0) via central differences
    println!("------------------------------------------------------------------------");
    println!("Evaluating 16x16 Tangent Map Jacobian J...");

    let eps = 1e-7;
    let mut jacobian = [[0.0; DIM]; DIM];

    for col in 0..DIM {
        let mut z_fwd = z0;
        let mut z_bwd = z0;
        z_fwd[col] += eps;
        z_bwd[col] -= eps;

        let res_fwd = integrate_state(&z_fwd, dt, steps);
        let res_bwd = integrate_state(&z_bwd, dt, steps);

        for row in 0..DIM {
            jacobian[row][col] = (res_fwd[row] - res_bwd[row]) / (2.0 * eps);
        }
    }

    // Canonical symplectic matrix J_sym = [[0, I], [-I, 0]]
    let mut j_sym = [[0.0; DIM]; DIM];
    for i in 0..N_SITES {
        j_sym[i][N_SITES + i] = 1.0;
        j_sym[N_SITES + i][i] = -1.0;
    }

    // Temp = J_sym * J
    let mut temp = [[0.0; DIM]; DIM];
    for i in 0..DIM {
        for j in 0..DIM {
            let mut sum = 0.0;
            for k in 0..DIM {
                sum += j_sym[i][k] * jacobian[k][j];
            }
            temp[i][j] = sum;
        }
    }

    // M = J^T * temp
    let mut m_prod = [[0.0; DIM]; DIM];
    for i in 0..DIM {
        for j in 0..DIM {
            let mut sum = 0.0;
            for k in 0..DIM {
                sum += jacobian[k][i] * temp[k][j];
            }
            m_prod[i][j] = sum;
        }
    }

    // Defect Matrix: E = M - J_sym
    let mut max_defect: f64 = 0.0;
    let mut frobenius_norm: f64 = 0.0;
    for i in 0..DIM {
        for j in 0..DIM {
            let diff = (m_prod[i][j] - j_sym[i][j]).abs();
            if diff > max_defect {
                max_defect = diff;
            }
            frobenius_norm += diff * diff;
        }
    }
    frobenius_norm = frobenius_norm.sqrt();

    println!("[AUDIT] Frobenius Defect ||J^T*J_sym*J - J_sym||_F : {:.3e}", frobenius_norm);
    println!("[AUDIT] Maximum Pointwise Defect                 : {:.3e}", max_defect);

    let tolerance = 1e-5;
    if max_defect < tolerance {
        println!("------------------------------------------------------------------------");
        println!("[VERDICT] ADMITTED — Symplectic 2-form dq ^ dp conserved.");
        println!("          Transformation is in Sp(16, R).");
        println!("========================================================================");
        std::process::exit(0);
    } else {
        println!("------------------------------------------------------------------------");
        println!("[VERDICT] REJECTED — Symplectic defect exceeded tolerance 1e-5.");
        println!("========================================================================");
        std::process::exit(1);
    }
}
