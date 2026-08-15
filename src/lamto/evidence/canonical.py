import hashlib
import json
import unicodedata


def _normalize(value):
    if value is None or isinstance(value, bool) or type(value) is int:
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("Canonical object keys must be strings.")
            key = unicodedata.normalize("NFC", key)
            if key in normalized:
                raise ValueError("Canonical object keys must remain unique after NFC normalization.")
            normalized[key] = _normalize(item)
        return normalized
    raise TypeError(f"Unsupported canonical value: {type(value).__name__}")


def canonical_bytes(payload) -> bytes:
    if not isinstance(payload, (dict, list)):
        raise TypeError("Canonical payload must be a dictionary or list.")
    return json.dumps(
        _normalize(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def payload_hash(payload) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()
