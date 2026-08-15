from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from .embedding import FaceEmbedderUnavailable, get_embedder
from .matching import MATCH_METRIC, match_face, match_plate
from .models import GateEvent
from .plates import normalize_plate


def require_face_calibration():
    if not settings.GATE_FACE_CALIBRATED:
        raise FaceEmbedderUnavailable("Face recognition calibration is incomplete.")


@dataclass(frozen=True)
class RecognitionOutcome:
    matched: bool
    display_name: str
    unit_label: str
    direction: str
    score: float | None
    event_id: int


def recognize_face(credential, image_bytes: bytes) -> RecognitionOutcome:
    require_face_calibration()
    device = credential.device
    result = get_embedder().embed(image_bytes)
    match = match_face(device.building, result.vector, model_name=result.model_name, model_version=result.model_version)
    event = GateEvent.objects.create(
        building=device.building, device=device, kind=GateEvent.Kind.FACE,
        direction=device.direction, occurred_at=timezone.now(), matched_occupancy=match.occupancy,
        model_name=result.model_name, model_version=result.model_version,
        match_metric=MATCH_METRIC, threshold_used=settings.GATE_FACE_MATCH_THRESHOLD,
        match_score=match.score,
    )
    return _outcome(match.occupancy, device, match.score, event)


def recognize_plate(credential, raw_text: str) -> RecognitionOutcome:
    device = credential.device
    normalized = normalize_plate(raw_text)
    plate = match_plate(device.building, normalized)
    occupancy = plate.occupancy if plate else None
    event = GateEvent.objects.create(
        building=device.building, device=device, kind=GateEvent.Kind.PLATE,
        direction=device.direction, occurred_at=timezone.now(), matched_plate=plate,
        matched_occupancy=occupancy, raw_plate_text=(raw_text or "")[:64],
        normalized_plate_text=normalized,
    )
    return _outcome(occupancy, device, None, event)


def _outcome(occupancy, device, score, event):
    return RecognitionOutcome(
        occupancy is not None, occupancy.user.display_name if occupancy else "",
        occupancy.unit.label if occupancy else "", device.direction, score, event.pk,
    )
