import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from eth_account import Account
from eth_account.messages import encode_typed_data


BYTES32_RE = re.compile(r"0x[0-9a-f]{64}\Z")
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def build_evidence_typed_data(event_id, event_type, payload_hash_hex, previous_hash_hex):
    if any(
        not isinstance(value, str) or not BYTES32_RE.fullmatch(value)
        for value in (event_id, payload_hash_hex, previous_hash_hex)
    ):
        raise ValueError("Evidence IDs and hashes must be lowercase 0x-prefixed bytes32 values.")
    if isinstance(event_type, bool) or not isinstance(event_type, int) or event_type not in range(1, 12):
        raise ValueError("Evidence event type must be an integer from 1 through 11.")
    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Evidence": [
                {"name": "eventId", "type": "bytes32"},
                {"name": "payloadHash", "type": "bytes32"},
                {"name": "previousHash", "type": "bytes32"},
                {"name": "eventType", "type": "uint8"},
            ],
        },
        "primaryType": "Evidence",
        "domain": {
            "name": "LamToEvidence",
            "version": "1",
            "chainId": settings.BLOCKCHAIN_CHAIN_ID,
            "verifyingContract": settings.EVIDENCE_CONTRACT_ADDRESS,
        },
        "message": {
            "eventId": event_id,
            "payloadHash": payload_hash_hex,
            "previousHash": previous_hash_hex,
            # Plain int so JSON/MetaMask eth_signTypedData_v4 never see an enum label.
            "eventType": int(event_type),
        },
    }


def normalize_signature(signature) -> str:
    if isinstance(signature, str):
        value = signature.removeprefix("0x")
        try:
            raw = bytearray(bytes.fromhex(value))
        except ValueError as exc:
            raise ValueError("Signature must be hexadecimal.") from exc
    elif isinstance(signature, (bytes, bytearray)):
        raw = bytearray(signature)
    else:
        raise ValueError("Signature must be bytes or hexadecimal.")
    if len(raw) != 65:
        raise ValueError("Signature must be exactly 65 bytes.")
    # Some signers return recovery id as 0 or 1; EIP-155 style uses 27/28.
    if raw[64] in (0, 1):
        raw[64] = raw[64] + 27
    r = int.from_bytes(raw[:32], "big")
    s = int.from_bytes(raw[32:64], "big")
    if not 0 < r < SECP256K1_N or not 0 < s <= SECP256K1_N // 2 or raw[64] not in (27, 28):
        raise ValueError("Signature is not canonical secp256k1.")
    return "0x" + raw.hex()


def recover_signer(typed_data, signature) -> str:
    return Account.recover_message(
        encode_typed_data(full_message=typed_data), signature=normalize_signature(signature)
    )


def _platform_account():
    key = getattr(settings, "PLATFORM_SIGNER_PRIVATE_KEY", "")
    if not key:
        raise ImproperlyConfigured("PLATFORM_SIGNER_PRIVATE_KEY is not configured.")
    return Account.from_key(key)


def platform_signer_address() -> str:
    return _platform_account().address


def platform_sign_evidence(event_id, event_type, payload_hash_hex, previous_hash_hex) -> str:
    if isinstance(payload_hash_hex, str) and not payload_hash_hex.startswith("0x"):
        payload_hash_hex = "0x" + payload_hash_hex
    typed_data = build_evidence_typed_data(
        event_id, event_type, payload_hash_hex, previous_hash_hex
    )
    signed = Account.sign_typed_data(_platform_account().key, full_message=typed_data)
    return normalize_signature(signed.signature.hex())
