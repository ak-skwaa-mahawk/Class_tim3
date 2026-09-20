#!/usr/bin/env python3
"""
anchor_taproot_digest.py — TMS-SPEC-084 Taproot Witness Commitment Generator

Parses the SHA-256 state vector digest from VERIFICATION_REPORT.md,
constructs a BIP-341/342 Tapscript leaf committing the state digest via OP_RETURN,
computes the TapTree root, applies the TapTweak to an internal key, and
derives the BIP-350 Bech32m witness output address (P2TR).
"""

import hashlib
import re
import sys
from typing import Tuple

# Standard secp256k1 parameters
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
LEAF_VERSION_TAPSCRIPT = 0xC0

# BIP-341 Provably Unspendable Internal Public Key (NUMS point)
# Generated via H = lift_x(sha256("Taproot NUMS"))
NUMS_INTERNAL_KEY_HEX = (
    "50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0"
)


def tagged_hash(tag: str, msg: bytes) -> bytes:
    tag_hash = hashlib.sha256(tag.encode("utf-8")).digest()
    return hashlib.sha256(tag_hash + tag_hash + msg).digest()


def point_add(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[int, int]:
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 != y2:
        return None
    if x1 == x2:
        m = (3 * x1 * x1 * pow(2 * y1, SECP256K1_P - 2, SECP256K1_P)) % SECP256K1_P
    else:
        m = ((y2 - y1) * pow(x2 - x1, SECP256K1_P - 2, SECP256K1_P)) % SECP256K1_P
    x3 = (m * m - x1 - x2) % SECP256K1_P
    y3 = (m * (x1 - x3) - y1) % SECP256K1_P
    return (x3, y3)


def point_mul(p: Tuple[int, int], k: int) -> Tuple[int, int]:
    res = None
    curr = p
    while k > 0:
        if k & 1:
            res = point_add(res, curr)
        curr = point_add(curr, curr)
        k >>= 1
    return res


def lift_x(x: int) -> Tuple[int, int]:
    if x >= SECP256K1_P:
        return None
    y_sq = (pow(x, 3, SECP256K1_P) + 7) % SECP256K1_P
    y = pow(y_sq, (SECP256K1_P + 1) // 4, SECP256K1_P)
    if pow(y, 2, SECP256K1_P) != y_sq:
        return None
    if y % 2 != 0:
        y = SECP256K1_P - y
    return (x, y)


# --- BIP-350 Bech32m Encoding ---
BECH32M_CONST = 0x2BC830A3
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_polymod(values):
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for val in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ val
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32m_create_checksum(hrp, data):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ BECH32M_CONST
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def encode_bech32m(hrp: str, witver: int, witprog: bytes) -> str:
    data = [witver] + convertbits(witprog, 8, 5)
    checksum = bech32m_create_checksum(hrp, data)
    return hrp + "1" + "".join([CHARSET[d] for d in data + checksum])


# --- Extraction & Taproot Assembly ---
def extract_digest_from_report(report_path: str = "VERIFICATION_REPORT.md") -> str:
    pattern = re.compile(r"[0-9a-fA-F]{64}")
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            for line in f:
                if "SHA-256" in line or "digest" in line.lower():
                    match = pattern.search(line)
                    if match:
                        return match.group(0).lower()
    except FileNotFoundError:
        print(f"[ERROR] Cannot locate '{report_path}'.", file=sys.stderr)
        sys.exit(1)

    print(f"[ERROR] No SHA-256 state digest found in '{report_path}'.", file=sys.stderr)
    sys.exit(1)


def create_taproot_commitment(digest_hex: str, internal_pubkey_hex: str = NUMS_INTERNAL_KEY_HEX):
    digest_bytes = bytes.fromhex(digest_hex)
    internal_pubkey_bytes = bytes.fromhex(internal_pubkey_hex)

    # Tapscript: OP_RETURN (0x6a) + OP_PUSHBYTES_32 (0x20) + 32-byte digest
    script = b"\x6a\x20" + digest_bytes
    compact_size = len(script)
    leaf_payload = bytes([LEAF_VERSION_TAPSCRIPT, compact_size]) + script
    tapleaf_hash = tagged_hash("TapLeaf", leaf_payload)

    # Single-leaf tree: TapBranch hash is simply the leaf hash
    taptweak = tagged_hash("TapTweak", internal_pubkey_bytes + tapleaf_hash)

    tweak_int = int.from_bytes(taptweak, "big")
    p_point = lift_x(int.from_bytes(internal_pubkey_bytes, "big"))
    tweak_point = point_mul(SECP256K1_G, tweak_int)
    q_point = point_add(p_point, tweak_point)

    q_x = q_point[0]
    output_key_bytes = q_x.to_bytes(32, "big")
    parity_bit = 1 if q_point[1] % 2 != 0 else 0

    # Control block for script-path spending: [LeafVersion | Parity] + InternalKey (32 bytes)
    control_byte = LEAF_VERSION_TAPSCRIPT | parity_bit
    control_block = bytes([control_byte]) + internal_pubkey_bytes

    mainnet_addr = encode_bech32m("bc", 1, output_key_bytes)
    testnet_addr = encode_bech32m("tb", 1, output_key_bytes)

    return {
        "state_digest": digest_hex,
        "script_hex": script.hex(),
        "tapleaf_hash": tapleaf_hash.hex(),
        "taptweak": taptweak.hex(),
        "internal_key": internal_pubkey_hex,
        "output_key": output_key_bytes.hex(),
        "parity": parity_bit,
        "control_block": control_block.hex(),
        "p2tr_mainnet": mainnet_addr,
        "p2tr_testnet_regtest": testnet_addr,
    }


def main():
    print("=" * 72)
    print("  TAPROOT WITNESS ANCHOR GENERATOR — TMS-SPEC-084 / Class_tim3")
    print("=" * 72)

    digest = extract_digest_from_report("VERIFICATION_REPORT.md")
    anchor = create_taproot_commitment(digest)

    print(f"[STATE]  Extracted Digest (SHA-256) : {anchor['state_digest']}")
    print(f"[LEAF]   Script (OP_RETURN <32B>)   : {anchor['script_hex']}")
    print(f"[HASH]   TapLeaf Hash (BIP-342)     : {anchor['tapleaf_hash']}")
    print(f"[TWEAK]  TapTweak Hash (BIP-341)    : {anchor['taptweak']}")
    print(f"[KEY]    NUMS Internal Key (P)      : {anchor['internal_key']}")
    print(f"[OUTPUT] Tweaked Output Key (Q)     : {anchor['output_key']}")
    print(f"[PARITY] Output Key Parity Bit      : {anchor['parity']}")
    print(f"[BLOCK]  Control Block (33 Bytes)   : {anchor['control_block']}")
    print("-" * 72)
    print(f"[ADDR]   Mainnet P2TR (Bech32m)     : {anchor['p2tr_mainnet']}")
    print(f"[ADDR]   Regtest/Testnet P2TR       : {anchor['p2tr_testnet_regtest']}")
    print("=" * 72)


if __name__ == "__main__":
    main()
