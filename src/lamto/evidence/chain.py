"""Web3 client for the EvidenceRegistry contract on the managed Besu network."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db import connection
from eth_account import Account
from eth_utils import to_checksum_address
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.middleware import ExtraDataToPOAMiddleware

# Stable PostgreSQL advisory-lock keys shared by worker replicas.
RELAYER_NONCE_LOCK_KEY = 0x4C414D54_4F524C59  # "LAMTORLY"
OWNER_NONCE_LOCK_KEY = 0x4C414D54_4F4F574E  # "LAMTOOWN"
RECEIPT_TIMEOUT_SECONDS = 60


class ChainClientError(Exception):
    """Base error for chain client operations."""


class ChainSubmissionError(ChainClientError):
    """Raised when a transaction is mined with a non-success receipt status."""


class ChainTimeoutError(ChainClientError):
    """Raised when a receipt is not available within the wait window."""


@dataclass(frozen=True)
class ChainRecord:
    payload_hash: str
    previous_hash: str
    event_type: int
    signer: str
    recorded_at: int


def _default_abi_path() -> Path:
    configured = getattr(settings, "EVIDENCE_REGISTRY_ABI_PATH", None)
    if configured:
        return Path(configured)
    # settings.BASE_DIR is src/lamto; project root is two levels up.
    return (
        Path(settings.BASE_DIR).resolve().parent.parent
        / "chain"
        / "out"
        / "EvidenceRegistry.sol"
        / "EvidenceRegistry.json"
    )


def _load_abi(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    abi = artifact.get("abi", artifact)
    if not isinstance(abi, list):
        raise ChainClientError(f"Invalid EvidenceRegistry ABI artifact at {path}")
    return abi


def _normalize_bytes32(value) -> str:
    if value is None:
        return "0x" + "00" * 32
    if isinstance(value, (bytes, bytearray)):
        return "0x" + bytes(value).hex()
    text = str(value)
    if text.startswith("0x"):
        return text.lower()
    return "0x" + text.lower()


def _payload_hash_for_chain(payload_hash: str) -> str:
    text = payload_hash.lower()
    if text.startswith("0x"):
        return text
    return "0x" + text


class EvidenceRegistryClient:
    """Lookup, submission, and owner signer management for EvidenceRegistry."""

    def __init__(
        self,
        *,
        rpc_url: str | None = None,
        contract_address: str | None = None,
        relayer_private_key: str | None = None,
        owner_private_key: str | None = None,
        abi_path: str | Path | None = None,
        chain_id: int | None = None,
        w3: Web3 | None = None,
    ):
        self.rpc_url = rpc_url or settings.BLOCKCHAIN_RPC_URL
        self.chain_id = int(chain_id or settings.BLOCKCHAIN_CHAIN_ID)
        address = contract_address or settings.EVIDENCE_CONTRACT_ADDRESS
        self.contract_address = to_checksum_address(address)
        raw_relayer = (
            relayer_private_key
            if relayer_private_key is not None
            else settings.BLOCKCHAIN_RELAYER_PRIVATE_KEY
        )
        raw_owner = (
            owner_private_key
            if owner_private_key is not None
            else settings.BLOCKCHAIN_CONTRACT_OWNER_PRIVATE_KEY
        )
        # Whitespace-only is unset (same as empty); never feed it to Account.from_key.
        self.relayer_private_key = (raw_relayer or "").strip()
        self.owner_private_key = (raw_owner or "").strip()
        path = Path(abi_path) if abi_path is not None else _default_abi_path()
        self.abi = _load_abi(path)
        self.w3 = w3 or Web3(Web3.HTTPProvider(self.rpc_url))
        # Besu QBFT embeds validator votes in extraData (>32 bytes); without this
        # middleware eth_getBlockByNumber fails with ExtraDataLengthError.
        if ExtraDataToPOAMiddleware not in self.w3.middleware_onion:
            try:
                self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            except ValueError:
                # Already present under another identity.
                pass
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        self.last_receipt: dict[str, Any] | None = None

    def find(self, event) -> ChainRecord | None:
        raw = self.contract.functions.records(event.event_id).call()
        payload_hash, previous_hash, event_type, signer, recorded_at = raw
        if int(recorded_at) == 0:
            return None
        return ChainRecord(
            payload_hash=_normalize_bytes32(payload_hash),
            previous_hash=_normalize_bytes32(previous_hash),
            event_type=int(event_type),
            signer=to_checksum_address(signer),
            recorded_at=int(recorded_at),
        )

    def submit(self, event) -> str:
        if not self.relayer_private_key:
            raise ChainClientError("BLOCKCHAIN_RELAYER_PRIVATE_KEY is not configured.")
        account = Account.from_key(self.relayer_private_key)
        signer = to_checksum_address(event.signer_address)
        function = self.contract.functions.recordEvidence(
            event.event_id,
            _payload_hash_for_chain(event.payload_hash),
            event.previous_hash,
            int(event.event_type),
            signer,
            event.signature,
        )
        tx_hash = self._send_locked(
            account=account,
            function=function,
            lock_key=RELAYER_NONCE_LOCK_KEY,
        )
        # Persist hash ASAP so recovery does not rely only on records(eventId)
        # if the receipt wait times out or the worker is interrupted.
        if getattr(event, "pk", None) is not None and not getattr(
            event, "transaction_hash", ""
        ):
            type(event).objects.filter(pk=event.pk).update(transaction_hash=tx_hash)
            event.transaction_hash = tx_hash
        receipt = self._wait_for_receipt(tx_hash)
        self.last_receipt = dict(receipt)
        if int(receipt.get("status", 0)) != 1:
            raise ChainSubmissionError(
                f"recordEvidence receipt status {receipt.get('status')} for {tx_hash}"
            )
        return tx_hash

    def set_signer(self, address, authorized: bool) -> str:
        if not self.owner_private_key:
            raise ChainClientError("BLOCKCHAIN_CONTRACT_OWNER_PRIVATE_KEY is not configured.")
        account = Account.from_key(self.owner_private_key)
        function = self.contract.functions.setAuthorizedSigner(
            to_checksum_address(address), bool(authorized)
        )
        tx_hash = self._send_locked(
            account=account,
            function=function,
            lock_key=OWNER_NONCE_LOCK_KEY,
        )
        receipt = self._wait_for_receipt(tx_hash)
        self.last_receipt = dict(receipt)
        if int(receipt.get("status", 0)) != 1:
            raise ChainSubmissionError(
                f"setAuthorizedSigner receipt status {receipt.get('status')} for {tx_hash}"
            )
        return tx_hash

    def _fee_fields(self) -> dict[str, int]:
        """Pick legacy gasPrice vs EIP-1559 fees from the active fork.

        Local Besu QBFT is Berlin-only (no londonBlock / baseFeePerGas).
        EIP-1559 type-2 txs are rejected with "Invalid transaction type".
        """
        latest = self.w3.eth.get_block("latest")
        base_fee = latest.get("baseFeePerGas") if hasattr(latest, "get") else None
        if base_fee is None and hasattr(latest, "baseFeePerGas"):
            base_fee = latest.baseFeePerGas
        if base_fee is not None:
            priority = self.w3.to_wei(1, "gwei")
            return {
                "maxFeePerGas": int(base_fee) * 2 + priority,
                "maxPriorityFeePerGas": priority,
            }
        # Pre-London / Berlin: type-0 legacy only.
        gas_price = self.w3.eth.gas_price
        if gas_price is None or int(gas_price) == 0:
            gas_price = self.w3.to_wei(1, "gwei")
        return {"gasPrice": int(gas_price)}

    def _send_locked(self, *, account, function, lock_key: int) -> str:
        """Allocate nonce under a shared advisory lock, then send_raw_transaction."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_lock(%s)", [lock_key])
            try:
                nonce = self.w3.eth.get_transaction_count(account.address, "pending")
                tx = function.build_transaction(
                    {
                        "from": account.address,
                        "nonce": nonce,
                        "chainId": self.chain_id,
                        "gas": 500_000,
                        **self._fee_fields(),
                    }
                )
                signed = account.sign_transaction(tx)
                raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
                tx_hash = self.w3.eth.send_raw_transaction(raw)
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [lock_key])
        return self.w3.to_hex(tx_hash)

    def _wait_for_receipt(self, tx_hash: str) -> dict[str, Any]:
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=RECEIPT_TIMEOUT_SECONDS, poll_latency=0.5
            )
        except TimeExhausted as exc:
            raise ChainTimeoutError(
                f"Timed out waiting for receipt of {tx_hash}"
            ) from exc
        except Exception as exc:  # pragma: no cover - provider-specific
            # Some providers raise generic exceptions on timeout.
            if "timeout" in str(exc).lower() or "timed out" in str(exc).lower():
                raise ChainTimeoutError(str(exc)) from exc
            raise
        # Convert AttributeDict / HexBytes into JSON-friendly structures for storage.
        return _receipt_to_dict(receipt)


def _receipt_to_dict(receipt) -> dict[str, Any]:
    """Convert web3 AttributeDict / HexBytes receipt into JSON-safe dict."""

    def convert(value):
        if value is None or isinstance(value, (str, int, bool, float)):
            return value
        if isinstance(value, (bytes, bytearray)):
            return "0x" + bytes(value).hex()
        # HexBytes and other hex-able non-strings
        if hasattr(value, "hex") and not isinstance(value, (str, int, bool)):
            try:
                hexed = value.hex()
                if isinstance(hexed, str):
                    return hexed if hexed.startswith("0x") else "0x" + hexed
            except Exception:
                pass
        if isinstance(value, dict) or hasattr(value, "items"):
            try:
                items = value.items()
            except Exception:
                items = dict(value).items()
            return {str(k): convert(v) for k, v in items}
        if isinstance(value, (list, tuple)):
            return [convert(item) for item in value]
        return value

    result = convert(receipt)
    if not isinstance(result, dict):
        result = dict(result)
    if "status" in result and result["status"] is not None:
        result["status"] = int(result["status"])
    if "blockNumber" in result and result["blockNumber"] is not None:
        result["blockNumber"] = int(result["blockNumber"])
    return result


def default_client() -> EvidenceRegistryClient:
    return EvidenceRegistryClient()
