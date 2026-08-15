import numpy as np
import pytest

from lamto.gate.crypto import (
    EmbeddingDecryptionError,
    open_embedding,
    seal_embedding,
)


def test_roundtrips_a_vector(settings):
    settings.GATE_EMBEDDING_KEY = "test-key"
    vector = np.arange(512, dtype=np.float32) / 512.0
    restored = open_embedding(seal_embedding(vector))
    assert np.allclose(restored, vector)
    assert restored.dtype == np.float32
    assert restored.shape == (512,)


def test_ciphertext_does_not_contain_the_raw_bytes(settings):
    settings.GATE_EMBEDDING_KEY = "test-key"
    vector = np.ones(8, dtype=np.float32)
    assert vector.tobytes() not in seal_embedding(vector)


def test_a_different_key_cannot_open_the_vector(settings):
    settings.GATE_EMBEDDING_KEY = "first-key"
    sealed = seal_embedding(np.ones(8, dtype=np.float32))
    settings.GATE_EMBEDDING_KEY = "second-key"
    with pytest.raises(EmbeddingDecryptionError):
        open_embedding(sealed)


def test_rejects_a_non_vector(settings):
    settings.GATE_EMBEDDING_KEY = "test-key"
    with pytest.raises(ValueError):
        seal_embedding(np.zeros((2, 2), dtype=np.float32))
    with pytest.raises(ValueError):
        seal_embedding([])
