import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit, User
from lamto.gate.devices import issue_credential
from lamto.gate.enrollment import submit_face_enrollment, submit_plate
from lamto.gate.models import FaceEnrollment, GateDevice, GateEvent, ReviewStatus
from lamto.gate.recognition import recognize_face, recognize_plate
from lamto.gate.review import approve_face, approve_plate
from lamto.gate.tests.fakes import face_bytes
from lamto.gate.tests.conftest import gate_storage  # noqa: F401

pytestmark = pytest.mark.django_db

def test_enrol_approve_recognize_and_purge(settings, gate_storage, monkeypatch):
    settings.GATE_FACE_EMBEDDER = 'lamto.gate.tests.fakes.FakeEmbedder'
    settings.GATE_EMBEDDING_KEY = 'e2e-key'
    settings.GATE_FACE_CALIBRATED = True
    monkeypatch.setattr('lamto.gate.enrollment.scan_with_clamav', lambda f: True)
    building = Building.objects.create(name='E2E')
    unit = Unit.objects.create(building=building, label='12A')
    resident = User.objects.create(email='r@example.com', display_name='Nguyen A')
    occupancy = ResidentOccupancy.objects.create(user=resident, unit=unit)
    manager = ManagementMembership.objects.create(user=User.objects.create(email='m@example.com'), building=building)
    device = GateDevice.objects.create(building=building, label='North', direction='ENTRY')
    credential, _ = issue_credential(device, manager)
    face = submit_face_enrollment(occupancy, SimpleUploadedFile('f.jpg', face_bytes('nguyen'), content_type='image/jpeg'))
    plate = submit_plate(occupancy, '51F-123.45')
    approve_face(face, manager); approve_plate(plate, manager)
    assert recognize_face(credential, face_bytes('nguyen')).matched
    assert recognize_plate(credential, '51F12345').matched
    settings.GATE_EVENT_RETENTION_HOURS = -1
    call_command('purge_gate_data')
    assert not GateEvent.objects.exists()
    assert FaceEnrollment.objects.get().status == ReviewStatus.APPROVED
