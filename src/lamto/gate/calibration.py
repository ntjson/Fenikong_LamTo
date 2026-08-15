from dataclasses import dataclass, field
import numpy as np
from .crypto import open_embedding
from .matching import unit_vector
from .models import FaceEnrollment, ReviewStatus

@dataclass
class CalibrationScores:
    genuine: list[float] = field(default_factory=list)
    impostor: list[float] = field(default_factory=list)

@dataclass(frozen=True)
class ThresholdRow:
    threshold: float; fmr: float; fnmr: float; genuine_accepted: int; impostor_accepted: int

def error_rates(scores, threshold):
    ia = sum(s >= threshold for s in scores.impostor); gr = sum(s < threshold for s in scores.genuine)
    return (ia / len(scores.impostor) if scores.impostor else 0.0, gr / len(scores.genuine) if scores.genuine else 0.0)

def sweep(scores, start, stop, step):
    return [ThresholdRow(round(start + i * step, 4), *error_rates(scores, round(start + i * step, 4)), sum(s >= round(start + i * step, 4) for s in scores.genuine), sum(s >= round(start + i * step, 4) for s in scores.impostor)) for i in range(int(round((stop - start) / step)) + 1)]

def score_pairs(building, probes, *, model_name, model_version):
    enrolled = {r.occupancy_id: unit_vector(open_embedding(r.embedding)) for r in FaceEnrollment.objects.filter(status=ReviewStatus.APPROVED, embedding__isnull=False, occupancy__unit__building=building, model_name=model_name, model_version=model_version)}
    if any(occupancy_id not in enrolled for occupancy_id, _ in probes):
        raise ValueError("Manifest occupancy is outside the selected building/model enrollment set.")
    scores = CalibrationScores()
    for occupancy_id, vector in probes:
        probe = unit_vector(vector)
        for enrolled_id, candidate in enrolled.items():
            if candidate.shape == probe.shape:
                (scores.genuine if enrolled_id == occupancy_id else scores.impostor).append(float(np.dot(probe, candidate)))
    return scores
