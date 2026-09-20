#include <stdio.h>
#include <math.h>

#define N_SITES 8
#define MASS 1.0
#define KAPPA 100.0
#define THETA_STAR -15.000000
#define OMEGA_0_HZ 79.0

/* Yoshida 4th-Order Analytical Weight Constants */
#define CBRT_2 1.25992104989487316477
#define W0 (-CBRT_2 / (2.0 - CBRT_2))
#define W1 (1.0 / (2.0 - CBRT_2))

static const double SUB_STEPS[3] = {W1, W0, W1};

void compute_forces(const double q[N_SITES], double f[N_SITES]) {
    for (int j = 0; j < N_SITES; j++) {
        double q_next = q[(j + 1) % N_SITES];
        double q_prev = q[(j - 1 + N_SITES) % N_SITES];
        f[j] = KAPPA * (q_next - 2.0 * q[j] + q_prev);
    }
}

void verlet_substep(double q[N_SITES], double p[N_SITES], double dt_sub) {
    double f[N_SITES];
    compute_forces(q, f);

    /* 1. Momentum half-kick */
    for (int j = 0; j < N_SITES; j++) {
        p[j] += 0.5 * dt_sub * f[j];
    }

    /* 2. Coordinate full-drift */
    for (int j = 0; j < N_SITES; j++) {
        q[j] += (dt_sub / MASS) * p[j];
    }

    /* 3. Momentum final half-kick */
    compute_forces(q, f);
    for (int j = 0; j < N_SITES; j++) {
        p[j] += 0.5 * dt_sub * f[j];
    }
}

void yoshida4_step(double q[N_SITES], double p[N_SITES], double dt) {
    for (int s = 0; s < 3; s++) {
        verlet_substep(q, p, SUB_STEPS[s] * dt);
    }
}

double compute_total_energy(const double q[N_SITES], const double p[N_SITES]) {
    double t_kin = 0.0;
    double v_pot = 0.0;

    for (int j = 0; j < N_SITES; j++) {
        t_kin += 0.5 * (p[j] * p[j]) / MASS;
        double diff = q[(j + 1) % N_SITES] - q[j];
        v_pot += 0.5 * KAPPA * (diff * diff);
    }
    return t_kin + v_pot;
}

int main(void) {
    double dt = (1.0 / OMEGA_0_HZ) / 200.0;
    int total_steps = 50000;

    double q[N_SITES];
    double p[N_SITES];

    /* Initialize displaced around the theta* = -15.000000 rad null point */
    for (int j = 0; j < N_SITES; j++) {
        q[j] = THETA_STAR + 0.05 * cos(2.0 * M_PI * j / N_SITES);
        p[j] = 0.0;
    }

    double h_initial = compute_total_energy(q, p);

    for (int step = 0; step < total_steps; step++) {
        yoshida4_step(q, p, dt);
    }

    double h_final = compute_total_energy(q, p);
    double rel_error = fabs(h_final - h_initial) / h_initial;

    printf("TMS-SPEC-084: Yoshida 4th-Order Integration Audit\n");
    printf("Initial Energy H_0 : %.12f J\n", h_initial);
    printf("Final Energy H_f   : %.12f J\n", h_final);
    printf("Relative Drift     : %.5e (Shadow Hamiltonian Bounded)\n", rel_error);
    printf("Null Orbit State   : q[0] = %.6f rad (Libration centered on theta*)\n", q[0]);

    return 0;
}
