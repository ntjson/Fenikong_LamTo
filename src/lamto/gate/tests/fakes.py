"""Deterministic embedder for tests: no model files, no network, no drift.

An image is a marker: ``b"FACE:<seed>"`` embeds as ``fake_vector(seed)``,
so a test controls similarity exactly. Use ``face_bytes(seed)`` to build one.
"""

import hashlib

import numpy as np

from lamto.gate.embedding import (
    EmbeddingResult,
    MultipleFacesDetected,
    NoFaceDetected,
)

FAKE_MODEL_NAME = "fake"
FAKE_MODEL_VERSION = "1"
VECTOR_SIZE = 512
_PREFIX = b"FACE:"


def face_bytes(seed: str) -> bytes:
    """Image bytes the fake embeds as ``fake_vector(seed)``."""
    return _PREFIX + seed.encode("utf-8")


def fake_vector(seed: str) -> list[float]:
    """Stable unit vector for a seed string."""
    rng = np.random.default_rng(
        int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8], "big")
    )
    vector = rng.standard_normal(VECTOR_SIZE).astype(np.float32)
    return (vector / np.linalg.norm(vector)).tolist()


class FakeEmbedder:
    def embed(self, image_bytes: bytes) -> EmbeddingResult:
        if image_bytes.startswith(b"NOFACE"):
            raise NoFaceDetected("No face in image.")
        if image_bytes.startswith(b"MANYFACES"):
            raise MultipleFacesDetected("More than one face in image.")
        if not image_bytes.startswith(_PREFIX):
            raise NoFaceDetected("No face in image.")
        seed = image_bytes[len(_PREFIX) :].decode("utf-8", "replace")
        return EmbeddingResult(
            vector=fake_vector(seed),
            model_name=FAKE_MODEL_NAME,
            model_version=FAKE_MODEL_VERSION,
            detection_score=0.99,
        )
