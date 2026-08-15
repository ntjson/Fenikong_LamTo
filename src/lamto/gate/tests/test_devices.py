from datetime import timedelta

import pytest
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from lamto.gate.devices import (
    GateAuthenticationFailed,
    GateCredentialExpired,
    GateCredentialRevoked,
    authenticate_device,
    issue_credential,
    revoke_credential,
    rotate_credential,
    token_from_header,
)
from lamto.gate.models import GateDevice, GateDeviceCredential

pytestmark = pytest.mark.django_db


@pytest.fixture
def device(building):
    return GateDevice.objects.create(
        building=building, label="North gate", direction=GateDevice.Direction.ENTRY
    )


def test_issue_returns_a_token_that_is_not_stored(device, management):
    credential, token = issue_credential(device, management)
    assert token
    assert token not in credential.token_sha256
    assert len(credential.token_sha256) == 64
    assert authenticate_device(token).pk == credential.pk


def test_authenticate_records_the_hour_the_reader_was_last_seen(device, management):
    _, token = issue_credential(device, management)
    authenticate_device(token)
    device.refresh_from_db()
    assert device.last_seen_hour is not None
    assert device.last_seen_hour.minute == 0
    assert device.last_seen_hour.second == 0
    assert device.last_seen_hour.microsecond == 0


def test_rotation_keeps_the_old_credential_alive_during_the_grace(device, management, settings):
    settings.GATE_CREDENTIAL_ROTATION_GRACE_HOURS = 24
    _, old = issue_credential(device, management)
    _, new = rotate_credential(device, management)
    assert authenticate_device(old) is not None
    assert authenticate_device(new) is not None


def test_rotation_with_zero_grace_invalidates_the_old_token_at_once(device, management, settings):
    settings.GATE_CREDENTIAL_ROTATION_GRACE_HOURS = 0
    _, old = issue_credential(device, management)
    _, new = rotate_credential(device, management)
    with pytest.raises(GateCredentialExpired):
        authenticate_device(old)
    assert authenticate_device(new) is not None


def test_the_old_credential_dies_when_the_grace_elapses(device, management, settings):
    settings.GATE_CREDENTIAL_ROTATION_GRACE_HOURS = 1
    credential, old = issue_credential(device, management)
    rotate_credential(device, management)
    GateDeviceCredential.objects.filter(pk=credential.pk).update(
        expires_at=timezone.now() - timedelta(minutes=1)
    )
    with pytest.raises(GateCredentialExpired):
        authenticate_device(old)


def test_revocation_is_immediate_and_has_no_grace(device, management):
    credential, token = issue_credential(device, management)
    revoke_credential(credential, management)
    with pytest.raises(GateCredentialRevoked):
        authenticate_device(token)


def test_an_unknown_token_does_not_reveal_whether_a_device_exists(device, management):
    issue_credential(device, management)
    with pytest.raises(GateAuthenticationFailed) as caught:
        authenticate_device("not-a-real-token")
    assert caught.value.code == "gate_device_unauthenticated"
    assert not isinstance(caught.value, (GateCredentialRevoked, GateCredentialExpired))


def test_a_deactivated_device_cannot_authenticate(device, management):
    _, token = issue_credential(device, management)
    GateDevice.objects.filter(pk=device.pk).update(active=False)
    with pytest.raises(GateAuthenticationFailed):
        authenticate_device(token)


def test_repeated_failures_from_one_address_are_throttled(device, management):
    for _ in range(5):
        with pytest.raises(GateAuthenticationFailed):
            authenticate_device("wrong", ip="203.0.113.7")
    with pytest.raises(PermissionDenied):
        authenticate_device("wrong", ip="203.0.113.7")


def test_header_parsing():
    assert token_from_header("GateDevice abc123") == "abc123"
    assert token_from_header("gatedevice abc123") == "abc123"
    assert token_from_header("Token abc123") == ""
    assert token_from_header("") == ""
    assert token_from_header(None) == ""
