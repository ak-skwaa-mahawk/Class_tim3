TMS-SPEC-085: Client-Facing Telemetry API & Dashboard Specification
Document Metadata
 * Specification ID: TMS-SPEC-085
 * Entity: Two Mile Solutions (TMS)
 * Underlying Architecture: Class_tim3 / Heterosis Substrate
 * Security & Clean-Room Boundary: TMS-LIC-084 / AGPL-3.0 Separation
 * Target Audience: External Integrators, Telemetry Dashboards, Autonomous Fleet Monitors
1. Architectural Overview & Abstraction Boundary
To protect proprietary dynamical parameters and avoid exposing raw Hamiltonian phase trajectories, the public-facing API acts as an abstraction gateway. The underlying real symplectic manifold \mathcal{M} = T^*Q \cong \mathbb{R}^{16} and its canonical 2-form \omega \in \mathrm{Sp}(16, \mathbb{R}) are completely masked behind high-level operational observables.
External clients interface strictly with normalized, non-reconstructible health indicators, consensus proofs, and aggregated execution throughput:
┌─────────────────────────────────────────────────────────────┐
│                 Client-Facing Application                   │
│        (Monitoring Dashboards, Fleet Controllers)           │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / WSS
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               TMS Telemetry Abstraction Gateway             │
│   - Obfuscates Sp(16, R) State Vectors                      │
│   - Normalizes Drift, Damping, and Resonance Metrics        │
│   - Serves Cryptographic Integrity Receipts                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ Internal IPC / MMIO
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Heterosis Substrate & Core Engine             │
│   - 16-Dimensional Symplectic Phase Integration             │
│   - Physical Restoring Precession Loop                      │
│   - On-Chain Taproot Anchor State                           │
└─────────────────────────────────────────────────────────────┘

2. Telemetry Mapping Matrix
The gateway maps proprietary or topologically sensitive engine variables to abstracted, standard engineering units:
| Internal Core Variable | Mathematical Domain | Public Dashboard Attribute | Public Unit / Format | Description |
|---|---|---|---|---|
| \mathbf{z} \in \mathbb{R}^{16} | \mathrm{Sp}(16, \mathbb{R}) Canonical Coordinates | system_stability_index | Float (0.000 to 1.000) | Normalized scalar tracking symplectic volume preservation. |
| \Delta\Omega | Angular Precession Error | clock_drift_bias_ppm | Float (\pm\text{PPM}) | Phase deviation relative to the 79.0 Hz nominal base cadence. |
| \tau_{\text{prec}} | Corrective Intake Torque | precession_effort_pct | Float (-100.0% to +100.0%) | Clamped control effort applied by the drift compensator. |
| E_k (Modes 1–8) | Modal Energy Partition | harmonic_energy_balance | Array of 8 Floats (Sum = 1.0) | Relative energy distribution across vibrational modes. |
| core_hash | Packed Binary Digest | state_digest | String (Hex-64) | Public cryptographic state hash. |
| Taproot Leaf Proof | BIP-341 Commitment | ledger_anchor_status | JSON Object | Confirmed block height, TXID, and attestation status. |
3. REST API Specification
Base URL: [https://api.twomilesolutions.com/v1/telemetry](https://api.twomilesolutions.com/v1/telemetry)
Authentication: Bearer Token (Authorization: Bearer <API_KEY>)
3.1 Get Current Telemetry State
Retrieves the latest instantaneous health snapshot of the node.
 * Endpoint: GET /state
 * Response: 200 OK
{
  "node_id": "node_alpha",
  "timestamp_ns": 1782137289000123456,
  "sequence": 1048576,
  "telemetry": {
    "stability_index": 0.99984,
    "clock_drift_bias_ppm": 0.082,
    "precession_effort_pct": -4.85,
    "intake_pressure_nominal_bar": 1.0142,
    "harmonic_energy_balance": [
      0.125, 0.124, 0.126, 0.125, 0.125, 0.125, 0.125, 0.125
    ]
  },
  "consensus": {
    "active_peer_count": 3,
    "network_heterosis_gain": 1.0000,
    "quorum_locked": true
  },
  "attestation": {
    "state_digest": "a44db35bc5f551211e68b497a0e8e8a3a4445ac60586e460a5a63f1f596caff8",
    "ledger_anchor": {
      "network": "signet",
      "block_height": 323031,
      "txid": "ee8da3f25f1e772144fc5d4ce40d6de9a4cf06d8cc3ba9ce7fdb42d1408eae14"
    }
  }
}

3.2 Query Peer Mesh Status
Returns connectivity status and synchronization health with neighboring nodes.
 * Endpoint: GET /peers
 * Response: 200 OK
{
  "node_id": "node_alpha",
  "peers": [
    {
      "peer_id": "node_beta",
      "status": "SYNCHRONIZED",
      "rtt_ms": 1.42,
      "phase_variance": 0.000012,
      "interlock_root": "3e027ab2a247e014e39f72b6a94f92d6e3c1a85b9f71c42e8d9a0f4e1c2b3a4d",
      "last_heartbeat_s_ago": 0.4
    }
  ]
}

4. WebSocket Streaming API
For real-time operational monitoring, clients connect to the streaming interface to receive high-frequency telemetry updates without polling overhead.
 * URL: wss://[api.twomilesolutions.com/v1/telemetry/stream](https://api.twomilesolutions.com/v1/telemetry/stream)
 * Protocols: v1.tms-telemetry
4.1 Subscription Handshake
Immediately upon establishing the WebSocket connection, the client must send an authentication and configuration frame:
{
  "action": "subscribe",
  "token": "eyJhbGciOiJIUzI1NiIsIn...",
  "channels": ["metrics", "consensus", "alerts"],
  "sample_rate_hz": 10
}

4.2 Outbound Metric Stream (metrics)
Emitted periodically at the negotiated cadence (sample_rate_hz):
{
  "event": "metric_sample",
  "seq": 1048580,
  "timestamp_ns": 1782137289400000000,
  "metrics": {
    "stability_index": 0.99982,
    "clock_drift_bias_ppm": 0.079,
    "precession_effort_pct": -4.71,
    "shear_recirculation_rate": 0.9994
  }
}

4.3 Quorum & Alert Events (alerts)
Emitted asynchronously when threshold boundary exceptions occur (e.g., peer drop, compensation clamp):
{
  "event": "system_alert",
  "level": "WARN",
  "code": "PRECESSION_LIMIT_APPROACH",
  "message": "Precession effort exceeded 85% of dynamic clamp boundary.",
  "context": {
    "effort_pct": 86.4,
    "recovery_strategy": "CHIRAL_DAMPING_ENGAGED"
  },
  "timestamp_ns": 1782137290120000000
}

5. Security & Rate Limiting Controls
 * Information Leakage Prevention: The API gateway strips any response field containing raw matrix eigenvalues, raw symplectic coordinates (q_i, p_i), or specific hardware memory offsets (0x4000_1000).
 * Replay Protection: Every WebSocket message and REST attestation response carries a monotonic sequence counter (seq) cryptographically tied to the engine's internal step count.
 * Rate Limiting:
   * REST endpoints: Maximum 60 requests per minute per API key.
   * WebSocket feeds: Throttled to a maximum outbound broadcast of 20 Hz per subscriber. Requests for raw sample-level data (e.g., 79.0 Hz full stream) require an enterprise-tier token and mutual TLS (mTLS).
