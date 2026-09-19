# Physics & Computational Science 482: Numerical Mechanics & Symplectic Systems
**Term:** Autumn 2026  
**Module:** Laboratory & Analytical Methods for Constrained Dynamic Systems  
**Course File:** `syllabus.md`

---

## 1. Course Overview & Pedagogical Scope

This course develops numerical methods for conservative Hamiltonian systems. Standard non-symplectic integrators (such as classical explicit Runge-Kutta schemes) systematically fail over secular timescales by introducing artificial dissipation or unphysical energy growth. This laboratory series focuses on:

1. The exact analytic treatment of discrete 1D lattices (coupled harmonic chains and acoustic phonon modes).
2. The preservation of Hamiltonian symplectic 2-forms via geometric integrators (Velocity Verlet).
3. The emergence of cumulative operational drift across multi-stage systems and the formal derivation of the effective geometric scale factor $\pi_{\text{eff}}$.

---

## 2. Mathematical & Physical Derivations

### 2.1 One-Dimensional Harmonic Lattice & Discrete Dispersion

Consider a closed, periodic one-dimensional chain of $N$ identical particles of mass $m$, each coupled to its nearest neighbors by linear springs with spring constant $\kappa$. Let $q_n(t)$ denote the displacement of particle $n$ from its equilibrium position, with periodic boundary conditions:

$$q_{n+N}(t) = q_n(t), \quad \forall n \in \mathbb{Z}$$

The Hamiltonian of the system is:

$$H(\mathbf{q}, \mathbf{p}) = \sum_{n=0}^{N-1} \frac{p_n^2}{2m} + \sum_{n=0}^{N-1} \frac{\kappa}{2} (q_{n+1} - q_n)^2$$

Canonical equations of motion yield the coupled second-order system:

$$m \ddot{q}_n = -\frac{\partial H}{\partial q_n} = \kappa (q_{n+1} - 2q_n + q_{n-1})$$

To diagonalize the system into uncoupled normal modes, we substitute the plane-wave ansatz:

$$q_n(t) = A e^{i(k n a - \omega t)}$$

where $a$ is the lattice equilibrium spacing, $k$ is the wavevector, and $\omega$ is the modal eigenfrequency. Substituting this into the equations of motion:

$$-m \omega^2 A e^{i(k n a - \omega t)} = \kappa A \left( e^{i k (n+1) a} - 2 e^{i k n a} + e^{i k (n-1) a} \right) e^{-i \omega t}$$

Factoring out $A e^{i(k n a - \omega t)}$:

$$-m \omega^2 = \kappa \left( e^{i k a} - 2 + e^{-i k a} \right) = \kappa \left( 2\cos(ka) - 2 \right) = -2\kappa (1 - \cos(ka))$$

Using the trigonometric identity $1 - \cos(\theta) = 2\sin^2\left(\frac{\theta}{2}\right)$:

$$-m \omega^2 = -4\kappa \sin^2\left(\frac{ka}{2}\right) \implies \omega(k) = 2 \sqrt{\frac{\kappa}{m}} \left\vert{} \sin\left(\frac{ka}{2}\right) \right\vert{}$$

For a finite discrete lattice of $N$ sites with periodic boundaries, the wavevector is quantized according to the first Brillouin zone:

$$k_j = \frac{2\pi j}{N a}, \quad j \in \left\{0, 1, \dots, N-1\right\}$$

Defining the normalized dispersion factor $d_j \in [0, 2]$:

$$d_j = 2 \left\vert{} \sin\left(\frac{j \pi}{N}\right) \right\vert{}$$

In an 8-site lattice ($N = 8$), the modal energy $E_j$ partitions across the discrete spectrum according to the projection of initial conditions onto the normal coordinate basis $Q_j(t) = \sum_n q_n(t) e^{-i k_j n a}$.

---

### 2.2 Symplectic Geometry & The Velocity Verlet Integrator

A continuous Hamiltonian flow $\phi_t: (q_0, p_0) \mapsto (q_t, p_t)$ preserves the differential 2-form (Poincaré invariant):

$$\omega^2 = \sum_{n=1}^N \mathrm{d}q_n \wedge \mathrm{d}p_n$$

A discrete numerical mapping $\Phi_{\Delta t}: (\mathbf{q}_n, \mathbf{p}_n) \mapsto (\mathbf{q}_{n+1}, \mathbf{p}_{n+1})$ is symplectic if and only if its Jacobian matrix $J = \frac{\partial(\mathbf{q}_{n+1}, \mathbf{p}_{n+1})}{\partial(\mathbf{q}_n, \mathbf{p}_n)}$ satisfies:

$$J^T \mathbb{J} J = \mathbb{J}, \quad \text{where } \mathbb{J} = \begin{pmatrix} 0 & I \\ -I & 0 \end{pmatrix}$$

#### Proof of Symplecticity for Velocity Verlet
For a separable Hamiltonian $H(\mathbf{q}, \mathbf{p}) = T(\mathbf{p}) + V(\mathbf{q})$ with force $\mathbf{F}(\mathbf{q}) = -\nabla V(\mathbf{q})$, the Velocity Verlet step is expressed as:

$$\mathbf{q}_{n+1} = \mathbf{q}_n + \mathbf{p}_n \frac{\Delta t}{m} + \frac{1}{2m} \mathbf{F}(\mathbf{q}_n) \Delta t^2$$

$$\mathbf{p}_{n+1} = \mathbf{p}_n + \frac{\Delta t}{2} \left[ \mathbf{F}(\mathbf{q}_n) + \mathbf{F}(\mathbf{q}_{n+1}) \right]$$

To analyze the transformation, decompose it into three elementary sub-steps:
1. **Momentum half-drift:** $\mathbf{p}' = \mathbf{p}_n + \frac{\Delta t}{2} \mathbf{F}(\mathbf{q}_n)$
2. **Coordinate full-drift:** $\mathbf{q}_{n+1} = \mathbf{q}_n + \frac{\Delta t}{m} \mathbf{p}'$
3. **Momentum second half-drift:** $\mathbf{p}_{n+1} = \mathbf{p}' + \frac{\Delta t}{2} \mathbf{F}(\mathbf{q}_{n+1})$

Computing differentials for each sub-step:

$$\mathrm{d}\mathbf{q}_n \wedge \mathrm{d}\mathbf{p}' = \mathrm{d}\mathbf{q}_n \wedge \left( \mathrm{d}\mathbf{p}_n + \frac{\Delta t}{2} \nabla \mathbf{F}(\mathbf{q}_n) \mathrm{d}\mathbf{q}_n \right) = \mathrm{d}\mathbf{q}_n \wedge \mathrm{d}\mathbf{p}_n + \frac{\Delta t}{2} \nabla \mathbf{F}(\mathbf{q}_n) (\mathrm{d}\mathbf{q}_n \wedge \mathrm{d}\mathbf{q}_n)$$

Since the wedge product of a differential 1-form with itself vanishes ($\mathrm{d}q_i \wedge \mathrm{d}q_i = 0$) and $\nabla \mathbf{F} = -\nabla^2 V$ is symmetric:

$$\mathrm{d}\mathbf{q}_n \wedge \mathrm{d}\mathbf{p}' = \mathrm{d}\mathbf{q}_n \wedge \mathrm{d}\mathbf{p}_n$$

Similarly, for the coordinate drift:

$$\mathrm{d}\mathbf{q}_{n+1} \wedge \mathrm{d}\mathbf{p}' = \left( \mathrm{d}\mathbf{q}_n + \frac{\Delta t}{m} \mathrm{d}\mathbf{p}' \right) \wedge \mathrm{d}\mathbf{p}' = \mathrm{d}\mathbf{q}_n \wedge \mathrm{d}\mathbf{p}'$$

And for the final momentum update:

$$\mathrm{d}\mathbf{q}_{n+1} \wedge \mathrm{d}\mathbf{p}_{n+1} = \mathrm{d}\mathbf{q}_{n+1} \wedge \left( \mathrm{d}\mathbf{p}' + \frac{\Delta t}{2} \nabla \mathbf{F}(\mathbf{q}_{n+1}) \mathrm{d}\mathbf{q}_{n+1} \right) = \mathrm{d}\mathbf{q}_{n+1} \wedge \mathrm{d}\mathbf{p}'$$

By transitivity:

$$\mathrm{d}\mathbf{q}_{n+1} \wedge \mathrm{d}\mathbf{p}_{n+1} = \mathrm{d}\mathbf{q}_n \wedge \mathrm{d}\mathbf{p}_n$$

Because the numerical map exactly conserves the canonical 2-form, backward error analysis demonstrates that Velocity Verlet does not solve the exact Hamiltonian $H$, but rather exactly solves a "shadow" or modified Hamiltonian $\widetilde{H} = H + \mathcal{O}(\Delta t^2)$. This bounds energy fluctuations for all simulation times without secular drift.

---

### 2.3 Compound Lattice Drift & Derivation of Effective Operating $\pi$ ($\pi_{\text{eff}}$)

When driven by a high-frequency baseline excitation $\Omega_0$ (e.g., $79.0\text{ Hz} \equiv 4737.60\text{ RPM}$), physical non-idealities across an $M$-stage lattice introduce small phase deviations:

$$\Delta \Omega = \sum_{m=1}^M \delta \omega_m$$

In ideal Euclidean geometry, the phase traversed during a single fundamental rotational period $T_0 = \frac{2\pi_0}{\Omega_0}$ satisfies the closed-orbit relation:

$$\theta(T_0) = \Omega_0 T_0 = 2\pi_0$$

When subject to compound rotational frequency drift $\Omega_{\text{eff}} = \Omega_0 + \Delta \Omega$, the actual physical period required to complete a cycle shifts to:

$$T_{\text{drift}} = \frac{2\pi_0}{\Omega_0 + \Delta \Omega}$$

If an observer or control algorithm tracks the system under the baseline time assumption $T_0$, the effective phase angle swept relative to the nominal circle geometry requires scaling the effective geometric ratio:

$$\theta_{\text{meas}} = \Omega_{\text{eff}} T_0 = (\Omega_0 + \Delta \Omega) \frac{2\pi_0}{\Omega_0} = 2\pi_0 \left(1 + \frac{\Delta \Omega}{\Omega_0}\right)$$

Equating the cycle to an effective perimeter-to-diameter ratio $\pi_{\text{eff}}$ mapped against the perturbed frequency space:

$$\pi_{\text{eff}} = \pi_0 \cdot \frac{\Omega_0}{\Omega_0 + \Delta \Omega} = \pi_0 \left(1 + \frac{\Delta \Omega}{\Omega_0}\right)^{-1}$$

Expanding as a Taylor series for small fractional drift $\left\vert{}\frac{\Delta \Omega}{\Omega_0}\right\vert{} \ll 1$:

$$\pi_{\text{eff}} = \pi_0 \left( 1 - \frac{\Delta \Omega}{\Omega_0} + \left(\frac{\Delta \Omega}{\Omega_0}\right)^2 - \mathcal{O}\left[\left(\frac{\Delta \Omega}{\Omega_0}\right)^3\right] \right)$$

#### Numerical Verification
Given:
- Baseline frequency: $\Omega_0 = 4737.60\text{ RPM}$ ($79.0\text{ Hz}$)
- Measured drift: $\Delta \Omega = +0.008000\text{ RPM}$
- Euclidean constant: $\pi_0 \approx 3.1415926535$

Calculate the fractional drift:

$$\frac{\Delta \Omega}{\Omega_0} = \frac{0.008000}{4737.60} \approx 1.6886 \times 10^{-6}$$

Applying the first-order expansion:

$$\pi_{\text{eff}} \approx 3.1415926535 \times (1 - 1.6886187 \times 10^{-6}) \approx 3.1415873$$

This matches the observed value calculated by `run_79hz_production_eval.py`.

---

## 3. Laboratory Assignment Schedule

| Week | Unit Topic | Laboratory Coding Deliverable | Assessment Target |
|---|---|---|---|
| **Week 1** | Hamiltonian Formalism & RK4 Failure | `rk4_energy_drift.py` | Observe $\mathcal{O}(t)$ secular energy growth |
| **Week 2** | Symplectic Integrators (Verlet / Leapfrog) | `verlet_integrator.py` | Verify 2-form conservation $\mathrm{d}q \wedge \mathrm{d}p$ |
| **Week 3** | 1D Harmonic Lattice (8-Site Model) | `lab_03_lattice.py` | Compute $E_k$ vs acoustic dispersion curve |
| **Week 4** | Spectral Visualization & Modes | `plot_lattice_spectrum.py` | Render clean SVG vector plot of energy modes |
| **Week 5** | Multi-Stage Drift & Screening Wardens | `run_79hz_production_eval.py` | Assert $\pm 0.005$ tolerance across all 8 stages |
| **Week 6** | State Hash Notarization & IPC Interfaces | `fpt_ipc_daemon.py` | Unix domain socket automated telemetry audit |

---

## 4. Grading Rubric & Submission Requirements

All work must be committed to the student repository (`Class_tim3`) on branch `main`.

1. **Analytical Derivations (30%)**: Complete mathematical derivations for dispersion and symplecticity documented in Markdown format with verified arithmetic.
2. **Source Code Implementation (40%)**: PEP-8 compliant Python scripts implementing symplectic updates without numerical library dependencies for core integration steps.
3. **Automated Verification Testing (20%)**: Passing status on all unit tests defined in `tests/test_invariants.py`.
4. **Visual & Notarized Artifacts (10%)**: Clean generated output files (`lattice_spectrum.svg`, `VERIFICATION_REPORT.md`) containing valid state hashes.
