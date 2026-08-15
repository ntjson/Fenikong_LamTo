from dataclasses import dataclass

import numpy as np
from django.conf import settings

from .crypto import VECTOR_DTYPE, open_embedding
from .models import FaceEnrollment, ReviewStatus, VehiclePlate

MATCH_METRIC = "cosine"


@dataclass(frozen=True)
class FaceMatch:
    occupancy: object | None
    score: float


def unit_vector(vector) -> np.ndarray:
    array = np.asarray(vector, dtype=VECTOR_DTYPE).ravel()
    norm = float(np.linalg.norm(array))
    if norm == 0:
        raise ValueError("Cannot match a zero-length embedding.")
    return array / norm


def match_face(building, vector, *, model_name: str, model_version: str) -> FaceMatch:
    probe = unit_vector(vector)
    rows = FaceEnrollment.objects.filter(
        status=ReviewStatus.APPROVED, embedding__isnull=False,
        model_name=model_name, model_version=model_version,
        occupancy__active=True, occupancy__unit__building=building,
    ).select_related("occupancy", "occupancy__unit")
    best, best_score = None, -1.0
    for row in rows:
        candidate = open_embedding(row.embedding)
        if candidate.shape == probe.shape:
            score = float(np.dot(probe, unit_vector(candidate)))
            if score > best_score:
                best, best_score = row.occupancy, score
    if best is None:
        return FaceMatch(None, 0.0)
    return FaceMatch(best if best_score >= settings.GATE_FACE_MATCH_THRESHOLD else None, best_score)


def match_plate(building, normalized: str):
    return VehiclePlate.objects.filter(
        building=building, plate=normalized, status=ReviewStatus.APPROVED,
        occupancy__active=True,
    ).select_related("occupancy", "occupancy__unit", "occupancy__user").first()
