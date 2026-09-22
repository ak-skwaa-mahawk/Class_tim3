TMS-SPEC-085_01: Partner Integration Guide (Tier B Commercial)
Document Overview
 * Document Ref: TMS-INTG-085-B
 * Target Audience: Tier B Commercial Integration Engineers, System Integrators, External Auditor Consortia
 * Governing Specification: TMS-SPEC-085_01 / Reference Core TMS-SPEC-084
 * Interface Protocol: REST (JSON) / WebSocket Streaming (JSON-Framed)
1. System Overview & Invariant Guarantees
Two Mile Solutions provides real-time telemetry verification via an abstracted, clean-room gateway interface. Internal dynamical transformations are computed within a symplectic 16-dimensional phase space \mathcal{M} \cong \mathbb{R}^{16} that preserves the canonical 2-form \omega.
To protect proprietary geometries while providing deterministic operational assurance, the external gateway eliminates raw coordinate outputs (q_i, p_i). Instead, downstream partners receive:
 * Normalized Symplectic Stability Index (S \in [0.000, 1.000]): A normalized measure of phase-volume conservation.
 * Normalized Modal Energy Partitions (\sum_{k=1}^8 E_k = 1.00000): Relative spectral energy distribution across the 8-stage boundary, stripped of absolute energy amplitudes.
 * Cryptographic Attestation Proofs: Merkle-anchored state commitments tied to a Bitcoin Signet transaction.
2. Telemetry Fields & Operational Semantics
2.1 Symplectic Stability Index (S)
The index S quantifies local phase space determinant preservation:
where \epsilon = 10^{-4} represents the nominal operating tolerance band.
| Range | Nominal Status | Recommended Integration Behavior |
|---|---|---|
| S \ge 0.98000 | Nominal (Locked) | Standard operation; symplectic preservation intact. |
| 0.90000 \le S < 0.98000 | Transient Settling | Permitted during initial spin-up, intake pressure adjustments, or mesh discovery cycles. |
| S < 0.90000 | Degraded Boundary | Excursion event detected; inspect precession_effort_pct and clock_drift_bias_ppm. |
| S = 0.00000 | Non-Symplectic State / Fault | Determinant divergence or non-finite inputs. Halt ingestion and trigger recovery. |
2.2 Modal Energy Partition (E_k)
The array harmonic_energy_balance delivers an 8-stage relative spectral energy distribution. The sum of all elements strictly equals unity:
Anomalous mechanical vibration, stage imbalance, or decoupling manifests as high-frequency modal shifts into higher indices (k \in [6, 8]) relative to nominal decay baselines.
3. API Reference & Verification Flow
3.1 REST: Inspect Current Node State
 * Method: GET
 * Path: /v1/telemetry/state
 * Sample Payload:
{
  "node_id": "node_primary",
  "timestamp_ns": 1790028333718978626,
  "sequence": 420,
  "telemetry": {
    "stability_index": 1.0,
    "clock_drift_bias_ppm": 0.04,
    "precession_effort_pct": 0.0,
    "intake_pressure_nominal_bar": 4.228,
    "harmonic_energy_balance": [
      0.12502,
      0.12500,
      0.12498,
      0.12500,
      0.12500,
      0.12500,
      0.12500,
      0.12500
    ]
  },
  "consensus": {
    "active_peer_count": 1,
    "network_heterosis_gain": 1.0,
    "quorum_locked": true
  },
  "attestation": {
    "state_digest": "7ab7fd4b1732b52c3c27e4df338eaeea5bb6ce3d539b83a2f8621a27eafe8ec7",
    "ledger_anchor": {
      "network": "signet",
      "block_height": 323031,
      "txid": "ee8da3f25f1e772144fc5d4ce40d6de9a4cf06d8cc3ba9ce7fdb42d1408eae14"
    }
  }
}

3.2 WebSocket Streaming Interface
 * Endpoint: ws://<host>:<port>/v1/telemetry/stream
Client Handshake
Upon establishing the connection, the client must transmit a JSON subscription frame specifying the desired sampling rate (clamped between 1 Hz and 60 Hz):
{
  "action": "subscribe",
  "sample_rate_hz": 10
}

Stream Frame Specification
{
  "event": "metric_sample",
  "seq": 421,
  "metrics": {
    "stability_index": 1.0,
    "precession_effort_pct": 0.0,
    "drift_ppm": 0.04,
    "pressure_bar": 4.228
  },
  "attestation_digest": "7ab7fd4b1732b52c3c27e4df338eaeea5bb6ce3d539b83a2f8621a27eafe8ec7"
}

Clients must enforce the following checks on every inbound frame:
 * Monotonic Sequence Ordering: Verify seq_{i} >= seq_{i-1}. Frame counter drops indicate dropped network frames or an upstream service restart.
 * Digest Continuity: Verify that attestation_digest matches the active ledger anchor.
4. On-Chain Ledger Verification (Signet Anchor)
To verify that telemetry emitted by an edge node corresponds to the authentic, mathematically certified specification without accessing internal IP:
 * Query Ledger Metadata: Extract ledger_anchor.txid and block_height from /v1/telemetry/state.
 * Retrieve Bitcoin Signet Transaction:
   Fetch transaction ee8da3f25f1e772144fc5d4ce40d6de9a4cf06d8cc3ba9ce7fdb42d1408eae14 from an independent Signet node or block explorer.
 * Validate P2TR Commitment Output:
   Locate the committed Pay-to-Taproot (P2TR) script output:
   * Target Address: tb1pg00dz9cgcx8rw44w3se62cmdm0ysdsf9u2ch3y9wyleancyxnhqsqaru9c
   * Inclusion Block: 323031
 * Attestation Leaf Check:
   Compute the double-SHA256 digest of your signed integration contract parameters against the committed leaf structure. The leaf inclusion confirms that the runtime metrics trace back to the verified root without revealing internal metrology parameters.
5. Partner Validation Script (Python Reference)
The following standalone script demonstrates subscription, frame parsing, bounds checking, and attestation extraction:
#!/usr/bin/env python3
import asyncio
import json
import websockets

GATEWAY_WS = "ws://127.0.0.1:8000/v1/telemetry/stream"
TARGET_SIGNET_TXID = "ee8da3f25f1e772144fc5d4ce40d6de9a4cf06d8cc3ba9ce7fdb42d1408eae14"

async def monitor_telemetry():
    async with websockets.connect(GATEWAY_WS) as ws:
        # 1. Send subscription handshake
        await ws.send(json.dumps({"action": "subscribe", "sample_rate_hz": 10}))
        
        last_seq = -1
        print("[*] Subscribed to TMS-SPEC-085_01 stream. Validating frames...")

        while True:
            raw_msg = await ws.recv()
            payload = json.loads(raw_msg)
            
            if payload.get("event") != "metric_sample":
                continue
                
            seq = payload["seq"]
            metrics = payload["metrics"]
            s_index = metrics["stability_index"]
            
            # Monotonic sequence check
            assert seq > last_seq, f"Sequence violation: {seq} <= {last_seq}"
            last_seq = seq
            
            # Operational bounds validation
            assert 0.0 <= s_index <= 1.0, f"Stability index out of range: {s_index}"
            status = "NOMINAL" if s_index >= 0.98 else "TRANSIENT" if s_index >= 0.90 else "DEGRADED"
            
            print(f"Frame #{seq:05d} | S={s_index:.5f} [{status}] | Drift={metrics['drift_ppm']} ppm")

if __name__ == "__main__":
    try:
        asyncio.run(monitor_telemetry())
    except KeyboardInterrupt:
        print("\nSession closed.")

