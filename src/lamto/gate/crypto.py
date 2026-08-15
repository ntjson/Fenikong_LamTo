"""Encryption for stored face embeddings.

Vectors are float32, serialized with ``ndarray.tobytes()`` and sealed with
Fernet before they reach the database. The Fernet key is derived from
``GATE_EMBEDDING_KEY`` so an operator can set any sufficiently random string
instead of a base64-encoded 32-byte blob.

Database compromise *combined with* key compromise exposes biometric
identifiers. Encryption at rest is not a substitute for the retention rules;
it is the floor under them.
"""

import base64
import hashlib

import numpy as np
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

VECTOR_DTYPE = np.float32


class EmbeddingDecryptionError(RuntimeError):
    """Stored embedding could not be opened with the configured key."""


def _fernet() -> Fernet:
    digest = hashlib.sha256(settings.GATE_EMBEDDING_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def seal_embedding(vector) -> bytes:
    array = np.asarray(vector, dtype=VECTOR_DTYPE)
    if array.ndim != 1 or array.size == 0:
        raise ValueError("Embedding must be a non-empty 1-D vector.")
    return _fernet().encrypt(array.tobytes())


def open_embedding(sealed: bytes) -> np.ndarray:
    try:
        raw = _fernet().decrypt(bytes(sealed))
    except InvalidToken as error:
        raise EmbeddingDecryptionError("Embedding could not be decrypted.") from error
    return np.frombuffer(raw, dtype=VECTOR_DTYPE)
