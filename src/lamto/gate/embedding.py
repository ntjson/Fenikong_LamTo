"""Face embedding boundary: one image in, one L2-normalized vector out.

The production implementation loads InsightFace; tests bind a deterministic
fake through ``GATE_FACE_EMBEDDER`` so CI needs no model files and no
network. Nothing outside this module knows which model is in use, which is
also what makes a model swap a configuration change plus a re-enrolment
rather than a rewrite.

The quality errors below are an IMAGE-QUALITY gate. They establish that an
image is usable. They are not identity assurance and not liveness detection,
and must never be described or relied on as either.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from django.conf import settings
from django.utils.module_loading import import_string


class FaceQualityError(ValueError):
    """Image is unusable. ``code`` is the resident-facing machine code."""

    code = "gate_face_unusable"


class NoFaceDetected(FaceQualityError):
    code = "gate_no_face_detected"


class MultipleFacesDetected(FaceQualityError):
    code = "gate_multiple_faces"


class FaceTooSmall(FaceQualityError):
    code = "gate_face_too_small"


class FaceTooBlurry(FaceQualityError):
    code = "gate_face_too_blurry"


class FaceEmbedderUnavailable(RuntimeError):
    """The model is not configured, could not load, or failed to run."""


@dataclass(frozen=True)
class EmbeddingResult:
    vector: list[float]
    model_name: str
    model_version: str
    detection_score: float


class FaceEmbedder(Protocol):
    def embed(self, image_bytes: bytes) -> EmbeddingResult: ...


def get_embedder() -> FaceEmbedder:
    path = settings.GATE_FACE_EMBEDDER
    if not path:
        raise FaceEmbedderUnavailable(
            "GATE_FACE_EMBEDDER is not set; refusing to guess a face model."
        )
    try:
        return import_string(path)()
    except Exception as exc:
        raise FaceEmbedderUnavailable(
            f"Could not load configured face embedder: {path}"
        ) from exc


class InsightFaceEmbedder:
    MODEL_NAME = "buffalo_l"
    _analysis = None

    @classmethod
    def _model(cls):
        if cls._analysis is None:
            try:
                from insightface.app import FaceAnalysis
                analysis = FaceAnalysis(name=cls.MODEL_NAME, allowed_modules=["detection", "recognition"], providers=["CPUExecutionProvider"])
                analysis.prepare(ctx_id=-1, det_size=(640, 640))
                cls._analysis = analysis
            except Exception as error:
                raise FaceEmbedderUnavailable(f"InsightFace model could not be loaded: {error}") from error
        return cls._analysis

    @property
    def model_version(self):
        import insightface
        return f"insightface-{insightface.__version__}"

    def embed(self, image_bytes: bytes) -> EmbeddingResult:
        import cv2
        import numpy as np
        image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise NoFaceDetected("Image could not be decoded.")
        try:
            faces = self._model().get(image)
        except FaceEmbedderUnavailable:
            raise
        except Exception as error:
            raise FaceEmbedderUnavailable(f"Face analysis failed: {error}") from error
        faces = [f for f in faces if float(f.det_score) >= settings.GATE_MIN_FACE_DET_SCORE]
        if not faces: raise NoFaceDetected("No face detected in the image.")
        if len(faces) > 1: raise MultipleFacesDetected("More than one face detected in the image.")
        face = faces[0]
        x1, y1, x2, y2 = (int(v) for v in face.bbox)
        if min(x2 - x1, y2 - y1) < settings.GATE_MIN_FACE_PIXELS: raise FaceTooSmall("The face is too small in the frame.")
        crop = image[max(y1, 0):max(y2, 0), max(x1, 0):max(x2, 0)]
        if crop.size and cv2.Laplacian(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var() < settings.GATE_MIN_FACE_SHARPNESS:
            raise FaceTooBlurry("The face is too blurry.")
        return EmbeddingResult(face.normed_embedding.tolist(), self.MODEL_NAME, self.model_version, float(face.det_score))
