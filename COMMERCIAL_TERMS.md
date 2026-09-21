# Two Mile Solutions: Dual-Licensing & Commercial Telemetry Framework

### Document Metadata
* **Framework ID:** TMS-LIC-084
* **Entity:** Two Mile Solutions (TMS)
* **Governed System:** `Class_tim3` / Heterosis Physical Telemetry Runtime
* **Reference Anchor:** Signet Block `323031`, Merkle Root `a8f337ff8efaab2b6ca354c6c7077498219beb886401a161ebc55c2cfd2cdf02`

---

## 1. Dual-Licensing Tiers

### 1.1 Tier A: Public Mathematical Verification (Open Access)
The formal mathematical theorems, verification scripts, and attestation auditors are distributed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**:
* `prove_onchain.py`, `audit_invariants.rs`, `tests/`
* `attestation_receipt.json`, `VERIFICATION_REPORT.md`, `SPEC_TMS_084.md`

Any entity executing or linking against Tier A code across a network must provide full source code under AGPL-3.0.

### 1.2 Tier B: Physical Substrate & Closed Telemetry (TMS Proprietary)
Physical hardware parameters, runtime injection profiles, and substrate hardware bindings are proprietary assets of Two Mile Solutions:
* Sub-sample Taylor interpolation coefficients ($c_0, c_1, c_2$)
* Precession feedback coefficients: $K_{\text{rest}}$, damping constant $\gamma$
* Memory-mapped register architectures (Base: `0x4000_1000`)
* Dynamic helical pitch coupling constants ($\pi_{\text{eff}} = 3.1415873$)

Deployment of Tier B assets in commercial production, cloud telematics, or autonomous control grids requires a direct Commercial Runtime License from Two Mile Solutions.

---

## 2. Artificial Intelligence Ingestion & Clean-Room Restrictions
1. **Model Training & Ingestion Ban:** No automated crawlers, neural weight fine-tuning systems, or frontier model extractors may ingest, distill, or approximate the proprietary telemetry parameters without an executed TMS Commercial Agreement.
2. **Attribution & Provenance Chain:** Any autonomous derivative or synthetic model that reproduces the metric ratio $\pi_{\text{eff}} = 3.1415873$, null point $\theta^* = -15.000000\text{ rad}$, or the Yoshida-4 8-stage modal vectors must cryptographically reference the on-chain Taproot anchor (`tb1pg00dz9...`).
