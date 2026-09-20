#!/usr/bin/env python3
"""build_anchor_psbt.py — Offline PSBT Generator for TMS-SPEC-084 State Anchors.

Constructs an unsigned raw transaction/PSBT committing to the P2TR output
and optional OP_RETURN carrier without holding signing keys.
"""

import argparse
import hashlib
import json
import sys


def parse_receipt(receipt_path: str) -> dict:
    with open(receipt_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_raw_anchor_tx(
    txin_txid: str,
    txin_vout: int,
    p2tr_address: str,
    digest_hex: str,
    amount_sats: int = 1000,
    fee_sats: int = 300,
    total_input_sats: int = 10000,
    change_address: str = "",
) -> None:
    # Marker payload: TMS1 (0x544d5331) + 32-byte digest
    marker = b"TMS1" + bytes.fromhex(digest_hex)

    print("=" * 72)
    print("  TMS-SPEC-084 OFFLINE ANCHOR TRANSACTION SPECIFICATION")
    print("=" * 72)
    print(f"[INPUT]   UTXO        : {txin_txid}:{txin_vout}")
    print(f"[INPUT]   Amount      : {total_input_sats} sats")
    print(f"[VOUT 0]  Commit P2TR : {p2tr_address} <- {amount_sats} sats")
    print(f"[VOUT 1]  Marker      : OP_RETURN 6a24{marker.hex()}")
    if change_address:
        change_sats = total_input_sats - amount_sats - fee_sats
        print(f"[VOUT 2]  Change P2TR : {change_address} <- {change_sats} sats")
    print(f"[FEE]     Network Fee : {fee_sats} sats")
    print("-" * 72)
    print("Execute via bitcoin-cli / Sparrow / HWI:")
    print(f"  bitcoin-cli -signet createrawtransaction \\")
    print(f"    '[{{\"txid\":\"{txin_txid}\",\"vout\":{txin_vout}}}]' \\")
    outputs = (
        f"    '[\"{p2tr_address}\": 0.00001000, \"data\": \"{marker.hex()}\""
    )
    if change_address:
        outputs += f", \"{change_address}\": {change_sats / 1e8:.8f}"
    outputs += "]'"
    print(outputs)
    print("=" * 72)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build TMS-SPEC-084 Anchor Transaction"
    )
    parser.add_argument(
        "--receipt",
        default="attestation_receipt.json",
        help="Path to attestation receipt",
    )
    parser.add_argument("--txin", required=True, help="Input UTXO txid:vout")
    parser.add_argument(
        "--input-sats",
        type=int,
        default=10000,
        help="Total satoshis in input UTXO",
    )
    parser.add_argument(
        "--change", default="", help="Change address for remaining balance"
    )
    args = parser.parse_args()

    txid_in, vout_in = args.txin.split(":")
    data = parse_receipt(args.receipt)
    addr = (
        data["p2tr_signet"]
        if data.get("network") == "signet"
        else data["p2tr_mainnet"]
    )
    build_raw_anchor_tx(
        txin_txid=txid_in,
        txin_vout=int(vout_in),
        p2tr_address=addr,
        digest_hex=data["digest_sha256"],
        total_input_sats=args.input_sats,
        change_address=args.change,
    )
