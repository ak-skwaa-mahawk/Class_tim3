// audit_invariants.rs — Independent Symplectic 2-Form & State Digest Auditor
// Links to libyoshida4.so to evaluate Jacobian J^T * J_sym * J == J_sym.

use std::os::raw::{c_double, c_int};

const N_SITES: usize = 8;
const DIM: usize = 2 * N_SITES; // Phase space dimension (16)

#[repr(C)]
pub struct YoshidaLatticeC {
    pub n_sites: c_int,
    pub mass: c_double,
    pub kappa: c_double,
    pub dt: c_double,
    pub q: [c_double; N_SITES],
    pub p: [c_double; N_SITES],
}

#[link(name = "yoshida4")]
extern "C" {
    pub fn c_yoshida4_init(
        lattice: *mut YoshidaLatticeC,
        n_sites: c_int,
        mass: c_double,
        kappa: c_double,
        dt: c_double,
    );
    pub fn c_yoshida4_step(lattice: *mut YoshidaLatticeC);
    pub fn c_yoshida4_hamiltonian(lattice: *const YoshidaLatticeC) -> c_double;
    pub fn c_yoshida4_integrate_chunk(lattice: *mut YoshidaLatticeC, steps: c_int);
}

/// Advance a 16-dimensional phase space state (q, p) through `steps` Yoshida-4 operations.
fn integrate_state(state: &[f64; DIM], mass: f64, kappa: f64, dt: f64, steps: i32) -> [f64; DIM] {
    let mut lattice = YoshidaLatticeC {
        n_sites: N_SITES as c_int,
        mass,
        kappa,
        dt,
        q: [0.0; N_SITES],
        p: [0.0; N_SITES],
    };

    unsafe {
        c_yoshida4_init(
            &mut lattice as *mut _,
            N_SITES as c_int,
            mass,
            kappa,
            dt,
        );
        for i in 0..N_SITES {
            lattice.q[i] = state[i];
            lattice.p[i] = state[N_SITES + i];
        }
        c_yoshida4_integrate_chunk(&mut lattice as *mut _, steps);
    }

    let mut out = [0.0; DIM];
    for i in 0..N_SITES {
        out[i] = lattice.q[i];
        out[N_SITES + i] = lattice.p[i];
    }
    out
}

fn compute_hamiltonian(state: &[f64; DIM], mass: f64, kappa: f64) -> f64 {
    let mut lattice = YoshidaLatticeC {
        n_sites: N_SITES as c_int,
        mass,
        kappa,
        dt: 0.0,
        q: [0.0; N_SITES],
        p: [0.0; N_SITES],
    };
    for i in 0..N_SITES {
        lattice.q[i] = state[i];
        lattice.p[i] = state[N_SITES + i];
    }
    unsafe { c_yoshida4_hamiltonian(&lattice as *const _) }
}

fn main() {
    println!("========================================================================");
    println!("  RUST SYMPLECTIC 2-FORM AUDITOR — TMS-SPEC-084 / Class_tim3");
    println!("========================================================================");

    let mass = 1.0;
    let kappa = 1.0;
    let dt = 0.005;
    let steps = 100; // 100 composition steps = 300 Verlet stages

    // Initial fiducial point centered around resonator null point (-15.0 rad)
    let mut z0 = [0.0; DIM];
    for i in 0..N_SITES {
        let theta = 2.0 * std::f64::consts::PI * (i as f64) / (N_SITES as f64);
        z0[i] = -15.0 + 0.15 * theta.sin();          // q_i
        z0[N_SITES + i] = 0.10 * theta.cos();        // p_i
    }

    let h0 = compute_hamiltonian(&z0, mass, kappa);
    let z_base_final = integrate_state(&z0, mass, kappa, dt, steps);
    let h_final = compute_hamiltonian(&z_base_final, mass, kappa);
    let rel_energy_err = ((h_final - h0) / h0).abs();

    println!("[FFI] Target Dynamic Library : libyoshida4.so (Loaded)");
    println!("[BASE] Step Count (Chunk)   : {} steps (dt = {})", steps, dt);
    println!("[BASE] Initial Energy H_0    : {:.12} J", h0);
    println!("[BASE] Final Energy H_t      : {:.12} J", h_final);
    println!("[DIFF] Delta H / H_0         : {:.3e}", rel_energy_err);

    // Compute numerical Jacobian J = d(z_final)/d(z_0) using central finite differences
    println!("------------------------------------------------------------------------");
    println!("Calculating 16x16 Phase Space Tangent Map (Jacobian J)...");

    let eps = 1e-7;
    let mut jacobian = [[0.0; DIM]; DIM];

    for col in 0..DIM {
        let mut z_fwd = z0;
        let mut z_bwd = z0;
        z_fwd[col] += eps;
        z_bwd[col] -= eps;

        let res_fwd = integrate_state(&z_fwd, mass, kappa, dt, steps);
        let res_bwd = integrate_state(&z_bwd, mass, kappa, dt, steps);

        for row in 0..DIM {
            jacobian[row][col] = (res_fwd[row] - res_bwd[row]) / (2.0 * eps);
        }
    }

    // Build canonical 2-form matrix J_sym = [[0, I], [-I, 0]]
    let mut j_sym = [[0.0; DIM]; DIM];
    for i in 0..N_SITES {
        j_sym[i][N_SITES + i] = 1.0;
        j_sym[N_SITES + i][i] = -1.0;
    }

    // Compute Product M = J^T * J_sym * J
    // Temp: T = J_sym * J
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

    // Evaluate Symplectic Defect Matrix: E = M - J_sym
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
    println!("[AUDIT] Max Pointwise 2-Form Defect               : {:.3e}", max_defect);

    let tolerance = 1e-6;
    if max_defect < tolerance {
        println!("------------------------------------------------------------------------");
        println!("[VERDICT] ADMITTED — Symplectic 2-form (dq ^ dp) strictly preserved.");
        println!("          Composite map resides on Sp(16, R) symplectic manifold.");
        println!("========================================================================");
        std::process::exit(0);
    } else {
        println!("------------------------------------------------------------------------");
        println!("[VERDICT] REJECTED — Symplectic defect exceeded threshold 1e-6.");
        println!("========================================================================");
        std::process::exit(1);
    }
}
