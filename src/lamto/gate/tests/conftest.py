import tempfile

import pytest

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit, User

FAKE_EMBEDDER_PATH = "lamto.gate.tests.fakes.FakeEmbedder"


@pytest.fixture
def gate_storage(settings):
    location = tempfile.mkdtemp(prefix="lamto-gate-")
    settings.STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": location}},
        "private": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": location}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    return location


@pytest.fixture
def use_fake_embedder(settings):
    settings.GATE_FACE_EMBEDDER = FAKE_EMBEDDER_PATH
    settings.GATE_EMBEDDING_KEY = "gate-test-key"
    settings.GATE_FACE_CALIBRATED = True
    return FAKE_EMBEDDER_PATH


@pytest.fixture
def building(db):
    return Building.objects.create(name="Gate Test Building")


@pytest.fixture
def occupancy(building):
    unit = Unit.objects.create(building=building, label="12A")
    user = User.objects.create(email="resident@example.com", display_name="Nguyen A")
    return ResidentOccupancy.objects.create(user=user, unit=unit)


@pytest.fixture
def second_occupancy(building):
    unit = Unit.objects.create(building=building, label="14B")
    user = User.objects.create(email="second@example.com", display_name="Tran B")
    return ResidentOccupancy.objects.create(user=user, unit=unit)


@pytest.fixture
def management(building):
    user = User.objects.create(email="manager@example.com", display_name="Manager")
    return ManagementMembership.objects.create(user=user, building=building)


@pytest.fixture
def clean_scanner():
    return lambda file_obj: True


@pytest.fixture
def infected_scanner():
    return lambda file_obj: False
