from datetime import UTC, datetime
from decimal import Decimal

from django.test import SimpleTestCase, override_settings
from eth_account import Account
from eth_account.messages import encode_typed_data

from lamto.evidence.canonical import canonical_bytes, payload_hash
from lamto.evidence.signatures import build_evidence_typed_data, recover_signer
from lamto.evidence.services import lowercase_identifier, normalize_vnd, utc_rfc3339


SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def high_s_signature(signature):
    raw = bytearray(signature)
    raw[32:64] = (SECP256K1_N - int.from_bytes(raw[32:64], "big")).to_bytes(32, "big")
    raw[64] = 27 if raw[64] == 28 else 28
    return "0x" + raw.hex()


@override_settings(
    BLOCKCHAIN_CHAIN_ID=1337,
    EVIDENCE_CONTRACT_ADDRESS="0x0000000000000000000000000000000000000001",
)
class EvidenceSignatureTests(SimpleTestCase):
    def test_canonical_payload_and_eip712_signature_recover_same_signer(self):
        account = Account.create()
        payload = {"amount_vnd": 18_500_000, "proposal_version": 2}
        typed = build_evidence_typed_data(
            event_id="0x" + "11" * 32,
            event_type=1,
            payload_hash_hex="0x" + payload_hash(payload),
            previous_hash_hex="0x" + "00" * 32,
        )
        signature = Account.sign_message(
            encode_typed_data(full_message=typed), account.key
        ).signature.hex()

        self.assertEqual(recover_signer(typed, signature), account.address)

    def test_recovery_rejects_high_s_and_malformed_signatures(self):
        account = Account.create()
        typed = build_evidence_typed_data(
            "0x" + "12" * 32, 1, "0x" + "34" * 32, "0x" + "00" * 32
        )
        signature = Account.sign_message(
            encode_typed_data(full_message=typed), account.key
        ).signature

        # v=0/1 are accepted (MetaMask) after normalize → 27/28; use v=2 as invalid.
        for invalid in (high_s_signature(signature), bytes(signature[:-1]), bytes(signature[:64]) + b"\x02"):
            with self.subTest(signature=invalid), self.assertRaises(ValueError):
                recover_signer(typed, invalid)

    def test_canonical_bytes_are_sorted_compact_utf8_and_nfc(self):
        self.assertEqual(
            canonical_bytes({"z": [True, None, 3], "a": "e\u0301"}),
            '{"a":"é","z":[true,null,3]}'.encode(),
        )

    def test_canonical_bytes_reject_unsupported_values_and_keys(self):
        invalid = (
            1,
            "text",
            {"value": 1.5},
            {"value": Decimal("1")},
            {"value": datetime.now(UTC)},
            {"value": b"bytes"},
            {1: "value"},
        )
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises((TypeError, ValueError)):
                canonical_bytes(payload)

    def test_payload_hash_is_lowercase_sha256_hex(self):
        digest = payload_hash({"amount_vnd": 1})
        self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_typed_data_exactly_matches_registry_contract(self):
        typed = build_evidence_typed_data(
            "0x" + "11" * 32, 11, "0x" + "22" * 32, "0x" + "00" * 32
        )

        self.assertEqual(
            typed,
            {
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
                    "chainId": 1337,
                    "verifyingContract": "0x0000000000000000000000000000000000000001",
                },
                "message": {
                    "eventId": "0x" + "11" * 32,
                    "payloadHash": "0x" + "22" * 32,
                    "previousHash": "0x" + "00" * 32,
                    "eventType": 11,
                },
            },
        )

    def test_typed_data_rejects_invalid_bytes32_and_event_types(self):
        valid_hash = "0x" + "00" * 32
        for event_id, event_type in (("0x12", 1), (valid_hash, 0), (valid_hash, 12), (valid_hash, True)):
            with self.subTest(event_id=event_id, event_type=event_type), self.assertRaises(
                ValueError
            ):
                build_evidence_typed_data(event_id, event_type, valid_hash, valid_hash)

    def test_service_payload_primitives_normalize_boundary_values(self):
        self.assertEqual(
            utc_rfc3339(datetime(2026, 7, 13, 8, 30, 1, 2, tzinfo=UTC)),
            "2026-07-13T08:30:01.000002Z",
        )
        self.assertEqual(lowercase_identifier("0xABCD"), "0xabcd")
        self.assertEqual(normalize_vnd(18_500_000), 18_500_000)
        with self.assertRaises((TypeError, ValueError)):
            normalize_vnd(Decimal("1"))
