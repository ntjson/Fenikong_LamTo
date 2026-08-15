import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from lamto.accounts.models import Building, ResidentOccupancy, Unit, User
from lamto.gate.models import (
    FaceEnrollment,
    GateDevice,
    GateEvent,
    ReviewStatus,
    VehiclePlate,
)


@pytest.fixture
def occupancy(db):
    building = Building.objects.create(name="Gate Test Building")
    unit = Unit.objects.create(building=building, label="12A")
    user = User.objects.create(email="resident@example.com", display_name="Resident")
    return ResidentOccupancy.objects.create(user=user, unit=unit)


def test_rejected_enrollment_cannot_keep_an_embedding(occupancy):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            FaceEnrollment.objects.create(
                occupancy=occupancy,
                embedding=b"sealed",
                status=ReviewStatus.REJECTED,
            )


def test_pending_enrollment_may_hold_an_embedding(occupancy):
    enrollment = FaceEnrollment.objects.create(
        occupancy=occupancy, embedding=b"sealed", status=ReviewStatus.PENDING
    )
    assert enrollment.pk is not None


def test_approved_plate_is_unique_per_building(occupancy):
    building = occupancy.unit.building
    other_unit = Unit.objects.create(building=building, label="14B")
    other_user = User.objects.create(email="other@example.com", display_name="Other")
    other = ResidentOccupancy.objects.create(user=other_user, unit=other_unit)
    VehiclePlate.objects.create(
        occupancy=occupancy,
        building=building,
        plate="51F12345",
        status=ReviewStatus.APPROVED,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            VehiclePlate.objects.create(
                occupancy=other,
                building=building,
                plate="51F12345",
                status=ReviewStatus.APPROVED,
            )


def test_pending_duplicates_are_allowed_until_approval(occupancy):
    building = occupancy.unit.building
    other_unit = Unit.objects.create(building=building, label="15C")
    other_user = User.objects.create(email="third@example.com", display_name="Third")
    other = ResidentOccupancy.objects.create(user=other_user, unit=other_unit)
    VehiclePlate.objects.create(
        occupancy=occupancy, building=building, plate="51F99999"
    )
    VehiclePlate.objects.create(occupancy=other, building=building, plate="51F99999")
    assert VehiclePlate.objects.filter(plate="51F99999").count() == 2


def _event(occupancy):
    building = occupancy.unit.building
    device = GateDevice.objects.create(
        building=building, label="North gate", direction=GateDevice.Direction.ENTRY
    )
    return GateEvent.objects.create(
        building=building,
        device=device,
        kind=GateEvent.Kind.PLATE,
        direction=device.direction,
        occurred_at=timezone.now(),
        raw_plate_text="51F-123.45",
        normalized_plate_text="51F12345",
    )


def test_gate_event_cannot_be_updated(occupancy):
    event = _event(occupancy)
    event.raw_plate_text = "tampered"
    with pytest.raises(Exception):
        with transaction.atomic():
            event.save(update_fields=["raw_plate_text"])


def test_gate_event_can_be_deleted(occupancy):
    event = _event(occupancy)
    event_id = event.pk
    event.delete()
    assert not GateEvent.objects.filter(pk=event_id).exists()
