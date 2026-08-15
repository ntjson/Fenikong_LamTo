import numpy as np
import pytest

from lamto.gate.embedding import (
    FaceEmbedderUnavailable,
    MultipleFacesDetected,
    NoFaceDetected,
    get_embedder,
)
from lamto.gate.tests.fakes import FakeEmbedder, face_bytes, fake_vector

FAKE_PATH = "lamto.gate.tests.fakes.FakeEmbedder"


def test_get_embedder_loads_the_configured_class(settings):
    settings.GATE_FACE_EMBEDDER = FAKE_PATH
    assert isinstance(get_embedder(), FakeEmbedder)


def test_get_embedder_refuses_to_guess_when_unset(settings):
    settings.GATE_FACE_EMBEDDER = ""
    with pytest.raises(FaceEmbedderUnavailable) as caught:
        get_embedder()
    assert caught.value.__cause__ is None


@pytest.mark.parametrize(
    ("path", "cause_type"),
    [
        ("missing.module.Embedder", ModuleNotFoundError),
        ("datetime.datetime", TypeError),
    ],
)
def test_get_embedder_translates_load_failures(settings, path, cause_type):
    settings.GATE_FACE_EMBEDDER = path
    with pytest.raises(FaceEmbedderUnavailable) as caught:
        get_embedder()
    assert isinstance(caught.value.__cause__, cause_type)


def test_fake_is_deterministic_and_unit_length():
    result = FakeEmbedder().embed(face_bytes("nguyen"))
    again = FakeEmbedder().embed(face_bytes("nguyen"))
    assert result.vector == again.vector
    assert np.isclose(np.linalg.norm(np.array(result.vector)), 1.0)


def test_distinct_seeds_are_near_orthogonal():
    a = np.array(fake_vector("a"))
    b = np.array(fake_vector("b"))
    assert abs(float(np.dot(a, b))) < 0.2


def test_fake_signals_the_quality_failures():
    with pytest.raises(NoFaceDetected):
        FakeEmbedder().embed(b"NOFACE")
    with pytest.raises(MultipleFacesDetected):
        FakeEmbedder().embed(b"MANYFACES")
    with pytest.raises(NoFaceDetected):
        FakeEmbedder().embed(b"a random jpeg")
