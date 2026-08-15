import pytest

from lamto.gate.embedding import InsightFaceEmbedder, NoFaceDetected

pytestmark = pytest.mark.insightface


def test_undecodable_image_is_reported_as_no_face():
    with pytest.raises(NoFaceDetected):
        InsightFaceEmbedder().embed(b"not an image")
