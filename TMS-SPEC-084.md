# TMS-SPEC-084: Mathematical Formalism & Analytical Derivations

This document details the governing equations, geometric mechanics proofs, and metrological propagation models underlying the `Class_tim3` experimental architecture.

---

## 1. Discrete Periodic Ring Lattice Dispersion Relation

Consider an $N$-site 1D periodic ring lattice of identical point masses $m$ connected by linear harmonic springs with coupling constant $\kappa$ and lattice spacing $a$. The discrete equation of motion for site $n \in \{0, 1, \dots, N-1\}$ is:

$$m \ddot{q}_n = \kappa (q_{n+1} - 2q_n + q_{n-1})$$

Applying periodic boundary conditions:

$$q_{n+N} = q_n$$

We postulate plane-wave normal mode solutions of the form:

$$q_n(t) = A e^{i(k n a - \omega t)}$$

where the allowed wave numbers are quantized by the ring geometry:

$$k_j = \frac{2\pi j}{N a}, \quad j \in \left\{0, 1, \dots, N-1\right\}$$

Substituting the ansatz into the equation of motion:

$$-m \omega^2 e^{i(k n a - \omega t)} = \kappa \left( e^{i k (n+1) a} - 2 e^{i k n a} + e^{i k (n-1) a} \right) e^{-i \omega t}$$

Dividing both sides by $m q_n(t)$:

$$-\omega^2 = \frac{\kappa}{m} \left( e^{i k a} - 2 + e^{-i k a} \right) = \frac{\kappa}{m} \left( 2\cos(ka) - 2 \right)$$

Using the half-angle trigonometric identity $1 - \cos(\phi) = 2\sin^2(\phi/2)$:

$$\omega^2(k) = \frac{4\kappa}{m} \sin^2\left(\frac{ka}{2}\right)$$

Taking the positive branch yields the discrete acoustic phonon dispersion relation:

$$\omega(k) = 2 \sqrt{\frac{\kappa}{m}} \left\vert{} \sin\left(\frac{ka}{2}\right) \right\vert{}$$

In the long-wavelength continuum limit ($k a \ll 1$), $\sin(ka/2) \approx ka/2$, retrieving the classical sound velocity $c_s = a\sqrt{\kappa/m}$:

$$\lim_{k \to 0} \frac{\omega(k)}{k} = a \sqrt{\frac{\kappa}{m}} = c_s$$

---

## 2. Symplectic 2-Form Preservation & Shadow Hamiltonian Bounds

The Hamiltonian of an uncoupled or linearly coupled mechanical chain on phase space $\mathcal{M} = \mathbb{R}^{2N}$ with canonical coordinates $(q, p)$ is:

$$H(q, p) = \frac{1}{2} p^T M^{-1} p + V(q) = T(p) + V(q)$$

A discrete time-stepping numerical map $\Phi_{\Delta t}: (q_t, p_t) \mapsto (q_{t+\Delta t}, p_{t+\Delta t})$ is **symplectic** if and only if its Jacobian matrix:

$$J = \frac{\partial(q_{t+\Delta t}, p_{t+\Delta t})}{\partial(q_t, p_t)}$$

preserves the canonical symplectic matrix $\mathbb{J} = \begin{pmatrix} 0 & I \\ -I & 0 \end{pmatrix}$:

$$J^T \mathbb{J} J = \mathbb{J} \iff \Phi_{\Delta t}^* \omega = \omega, \quad \text{where } \omega = \sum_{i=1}^N \mathrm{d}q_i \wedge \mathrm{d}p_i$$

### 2.1 Elementary Störmer-Verlet Step
The velocity Verlet map decomposes the time step $\Delta t$ into three sub-transformations:
1. $p_{t+1/2} = p_t - \frac{\Delta t}{2} \nabla V(q_t)$
2. $q_{t+1} = q_t + \Delta t M^{-1} p_{t+1/2}$
3. $p_{t+1} = p_{t+1/2} - \frac{\Delta t}{2} \nabla V(q_{t+1})$

Computing the differential exterior 2-form step-by-step:

$$\mathrm{d}p_{t+1/2} = \mathrm{d}p_t - \frac{\Delta t}{2} \nabla^2 V(q_t) \mathrm{d}q_t$$

$$\mathrm{d}q_t \wedge \mathrm{d}p_{t+1/2} = \mathrm{d}q_t \wedge \left(\mathrm{d}p_t - \frac{\Delta t}{2} \nabla^2 V(q_t) \mathrm{d}q_t\right) = \mathrm{d}q_t \wedge \mathrm{d}p_t$$

because the wedge product of identical 1-forms vanishes ($\mathrm{d}q \wedge \mathrm{d}q = 0$). Similarly, step (2) and step (3) each preserve the 2-form:

$$\mathrm{d}q_{t+1} \wedge \mathrm{d}p_{t+1} = \mathrm{d}q_{t+1} \wedge \mathrm{d}p_{t+1/2} = \mathrm{d}q_t \wedge \mathrm{d}p_{t+1/2} = \mathrm{d}q_t \wedge \mathrm{d}p_t$$

### 2.2 Yoshida 4th-Order Composition
Yoshida's symmetric composition combines three 2nd-order Störmer-Verlet maps $\mathcal{S}(\tau)$:

$$\Phi_{\text{Yoshida4}}(\Delta t) = \mathcal{S}(w_1 \Delta t) \circ \mathcal{S}(w_0 \Delta t) \circ \mathcal{S}(w_1 \Delta t)$$

To eliminate 2nd-order and 3rd-order error terms in the Baker-Campbell-Hausdorff (BCH) expansion, the step weights must satisfy:

$$2w_1 + w_0 = 1, \quad 2w_1^3 + w_0^3 = 0$$

Solving analytically:

$$w_0 = -\frac{2^{1/3}}{2 - 2^{1/3}}, \quad w_1 = \frac{1}{2 - 2^{1/3}}$$

Because each $\mathcal{S}(\tau)$ is symplectic, the composite map is strictly symplectic. By backward error analysis, $\Phi_{\text{Yoshida4}}$ exactly integrates a perturbed **Shadow Hamiltonian**:

$$\widetilde{H}(q, p) = H(q, p) + (\Delta t)^4 H_4(q, p) + \mathcal{O}((\Delta t)^6)$$

Because $\widetilde{H}$ is an exact invariant of the numerical map, the true physical energy error cannot drift secularly and remains globally bounded:

$$\left\vert{} H(q_t, p_t) - H(q_0, p_0) \right\vert{} \le C (\Delta t)^4, \quad \forall t \in [0, \infty)$$

---

## 3. Circle Metric Ratio ($\pi_{\text{eff}}$) & Operational Resonator Drift

In an unperturbed mechanical carrier operating at baseline frequency $\Omega_0$ (corresponding to $4737.60\text{ RPM}$ or $78.96\text{ Hz}$), the phase evolution $\theta(t)$ over a period $T_0$ maps to a Euclidean circle:

$$\oint \mathrm{d}\theta = \Omega_0 T_0 = 2\pi_0$$

When the physical driver sustains an operational frequency drift $\Delta \Omega = \Omega_{\text{meas}} - \Omega_0$, the empirical angular velocity becomes $\Omega = \Omega_0 + \Delta \Omega$. 

To map the dynamical recurrence metric to the physical rest frame, we define the **effective circle metric ratio** $\pi_{\text{eff}}$ such that the normalized action scale per cycle satisfies:

$$\pi_{\text{eff}} = \pi_0 \left(1 + \frac{\Delta \Omega}{\Omega_0}\right)^{-1}$$

### First-Order Taylor Approximation
For small fractional operating drifts ($\Delta \Omega / \Omega_0 \ll 1$):

$$\pi_{\text{eff}} = \pi_0 \left( 1 - \frac{\Delta \Omega}{\Omega_0} + \left(\frac{\Delta \Omega}{\Omega_0}\right)^2 - \dots \right)$$

Evaluating for the nominal parameters:
- $\Omega_0 = 4737.600000\text{ RPM}$
- $\Delta\Omega = +0.008000\text{ RPM}$
- Fractional drift: $\frac{\Delta\Omega}{\Omega_0} = \frac{0.008}{4737.60} \approx 1.6886 \times 10^{-6}$ ($1.69\text{ ppm}$)

$$\pi_{\text{eff}} = 3.1415926535 \times \left(1 - 1.6886187 \times 10^{-6}\right) \approx 3.1415873486\dots$$

### Resonator Null Point ($\theta^*$)
A phase-locking resonator with a nominal geometric phase offset $\phi_0 = 0.12\text{ rad}$ experiences a phase-space stagnation point $\theta^*$ where the accumulated drift rate counterbalances the geometric shear:

$$\theta^* = -\frac{\phi_0}{\Delta \Omega} = -\frac{0.12}{0.008000} = -15.000000\text{ rad}$$

This establishes the central libration coordinate around which the invariant phase torus remains bounded.

---

## 4. Metrology & GUM Uncertainty Propagation Architecture

To distinguish the physical drift $\Delta \Omega = 0.008\text{ RPM}$ ($1.69\text{ ppm}$) from measurement noise, uncertainties must be evaluated under the standard ISO/IEC Guide to the Expression of Uncertainty in Measurement (GUM).

### 4.1 Type A (Statistical) Uncertainty
From $N$ successive zero-crossing intervals $\Delta t_i$, the mean period is $\bar{T} = \frac{1}{N}\sum \Delta t_i$ with sample standard deviation $s_T$. Incorporating clock edge jitter $\sigma_{\text{jitter}}$:

$$u_A(\bar{T}) = \frac{s_T}{\sqrt{N}} + \frac{\sigma_{\text{jitter}}}{\sqrt{N}}$$

Using functional propagation for $\Omega = 60 / \bar{T}$:

$$u_A(\Omega) = \left\vert{} \frac{\partial \Omega}{\partial \bar{T}} \right\vert{} u_A(\bar{T}) = \frac{60}{\bar{T}^2} u_A(\bar{T})$$

### 4.2 Type B (Systematic) Uncertainty
Type B uncertainty incorporates non-statistical instrumentation limits:
- Timebase oscillator drift: $u_{\text{timebase}}$ (e.g., $1.0 \times 10^{-7}$)
- Rotary encoder grating error: $u_{\text{grating}}$ (e.g., $1.0 \times 10^{-7}$)
- Resonator thermal expansion: $u_{\text{thermal}} = \alpha \Delta T$ (e.g., $11.5\text{ ppm/K} \times 0.02\text{ K} = 2.3 \times 10^{-7}$)

The relative systematic uncertainty is:

$$u_{B,\text{rel}} = \sqrt{ u_{\text{timebase}}^2 + u_{\text{grating}}^2 + (\alpha \Delta T)^2 }$$

$$u_B(\Omega) = \Omega \cdot u_{B,\text{rel}}$$

### 4.3 Combined Uncertainty & Hypothesis Gating
The combined standard uncertainty of the measured speed is:

$$u_c(\Omega) = \sqrt{ u_A(\Omega)^2 + u_B(\Omega)^2 }$$

Propagating into $\pi_{\text{eff}}$ via the sensitivity coefficient $c_\Omega = \left\vert{}\frac{\partial \pi_{\text{eff}}}{\partial \Omega}\right\vert{}$:

$$c_\Omega = \frac{\pi_0}{\Omega_0 \left(1 + \frac{\Delta\Omega}{\Omega_0}\right)^2}$$

$$u_c(\pi_{\text{eff}}) = c_\Omega \cdot u_c(\Omega)$$

### 4.4 Acceptance Gate (SNR and $z$-Score)
A claim of physical operational drift is admitted if and only if both conditions are satisfied:

$$\text{SNR} = \frac{\vert{}\Delta \Omega\vert{}}{u_c(\Omega)} \ge 2.0$$

$$z = \frac{\vert{}\pi_{\text{eff}} - \pi_0\vert{}}{u_c(\pi_{\text{eff}})} \ge 2.0$$

If $z < 2.0$ or $\text{SNR} < 2.0$, the measurement is statistically indistinguishable from Euclidean $\pi_0$ at the 95% confidence level, rejecting the presence of physical drift.
