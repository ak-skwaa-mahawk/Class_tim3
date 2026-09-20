/* src/yoshida4_api.c */
#include <math.h>
#include <stddef.h>

#define N_SITES 8
#define MASS 1.0
#define KAPPA 100.0

#define CBRT_2 1.25992104989487316477
#define W0 (-CBRT_2 / (2.0 - CBRT_2))
#define W1 (1.0 / (2.0 - CBRT_2))

static const double SUB_STEPS[3] = {W1, W0, W1};

static void compute_forces(const double q[N_SITES], double f[N_SITES]) {
    for (int j = 0; j < N_SITES; j++) {
        double q_next = q[(j + 1) % N_SITES];
        double q_prev = q[(j - 1 + N_SITES) % N_SITES];
        f[j] = KAPPA * (q_next - 2.0 * q[j] + q_prev);
    }
}

static void verlet_substep(double q[N_SITES], double p[N_SITES], double dt_sub) {
    double f[N_SITES];
    compute_forces(q, f);

    for (int j = 0; j < N_SITES; j++) {
        p[j] += 0.5 * dt_sub * f[j];
    }
    for (int j = 0; j < N_SITES; j++) {
        q[j] += (dt_sub / MASS) * p[j];
    }
    compute_forces(q, f);
    for (int j = 0; j < N_SITES; j++) {
        p[j] += 0.5 * dt_sub * f[j];
    }
}

/* Exported symbols for Python ctypes */
void c_yoshida4_step(double *q, double *p, double dt) {
    for (int s = 0; s < 3; s++) {
        verlet_substep(q, p, SUB_STEPS[s] * dt);
    }
}

void c_yoshida4_integrate_chunk(double *q, double *p, double dt, int steps) {
    for (int i = 0; i < steps; i++) {
        for (int s = 0; s < 3; s++) {
            verlet_substep(q, p, SUB_STEPS[s] * dt);
        }
    }
}

double c_compute_hamiltonian(const double *q, const double *p) {
    double t_kin = 0.0;
    double v_pot = 0.0;
    for (int j = 0; j < N_SITES; j++) {
        t_kin += 0.5 * (p[j] * p[j]) / MASS;
        double diff = q[(j + 1) % N_SITES] - q[j];
        v_pot += 0.5 * KAPPA * (diff * diff);
    }
    return t_kin + v_pot;
}
