from unittest.mock import Mock, patch

import pytest
from django.test import override_settings
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.urls import reverse

from lamto.gate.models import GateDevice
from lamto.gate.tests.conftest import building, clean_scanner, gate_storage, management, occupancy, use_fake_embedder  # noqa: F401
from lamto.gate.tests.test_review import _enrol
from lamto.web.views.gate import gate_devices


def test_device_credential_actions_require_recent_reauthentication():
    request = RequestFactory().post("/s/gate/devices", {"action": "rotate", "device": "1"})
    request.user = Mock(is_authenticated=True)
    with patch("lamto.web.views.gate.require_management_context", return_value=(Mock(), [])), patch("lamto.web.views.gate.require_recent_auth", side_effect=PermissionDenied), pytest.raises(PermissionDenied):
        gate_devices(request)


@pytest.mark.django_db
def test_pending_face_photo_is_never_cached(client, occupancy, management, use_fake_embedder, gate_storage, clean_scanner):
    enrollment = _enrol(occupancy, clean_scanner)
    client.force_login(management.user)
    with patch("lamto.accounts.middleware.require_staff_mfa"), patch("lamto.web.staff.require_staff_mfa"):
        response = client.get(reverse("web:gate-face-photo", args=[enrollment.pk]))
    assert response.status_code == 200
    assert response["Cache-Control"] == "private, no-store"
    assert response["Pragma"] == "no-cache"


@pytest.mark.django_db
@override_settings(LANGUAGE_CODE="en")
def test_gate_review_renders_navigation_and_accessible_busy_decision_forms(
    client, occupancy, management, use_fake_embedder, gate_storage, clean_scanner
):
    enrollment = _enrol(occupancy, clean_scanner)
    client.force_login(management.user)
    with patch("lamto.accounts.middleware.require_staff_mfa"), patch("lamto.web.staff.require_staff_mfa"):
        response = client.get(reverse("web:gate-queue"))

    html = response.content.decode()
    assert response.status_code == 200
    assert 'aria-label="Gate"' in html
    assert reverse("web:gate-devices") in html
    assert reverse("web:gate-log") in html
    assert f'for="face-reject-reason-{enrollment.pk}"' in html
    assert f'id="face-reject-reason-{enrollment.pk}"' in html
    assert html.count("data-busy-on-submit") >= 2


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["web:gate-devices", "web:gate-log"])
def test_gate_record_pages_use_responsive_task_lists(client, management, url_name):
    client.force_login(management.user)
    with patch("lamto.accounts.middleware.require_staff_mfa"), patch("lamto.web.staff.require_staff_mfa"):
        response = client.get(reverse(url_name))

    html = response.content.decode()
    assert response.status_code == 200
    assert 'class="task-list"' in html
    assert "<table" not in html


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("label", "direction"),
    [("", GateDevice.Direction.ENTRY), ("   ", GateDevice.Direction.ENTRY), ("North", "entry"), ("North", "SIDEWAYS"), ("North", "")],
)
def test_invalid_reader_is_not_created_and_reports_error(client, management, label, direction):
    client.force_login(management.user)
    with patch("lamto.accounts.middleware.require_staff_mfa"), patch("lamto.web.staff.require_staff_mfa"), patch("lamto.web.views.gate.require_recent_auth"):
        response = client.post(reverse("web:gate-devices"), {"action": "create", "label": label, "direction": direction}, follow=True)
    assert response.redirect_chain == [(reverse("web:gate-devices"), 302)]
    assert GateDevice.objects.count() == 0
    assert b'aria-labelledby="messages-heading"' in response.content
    assert b'role="alert"' not in response.content


@pytest.mark.django_db
@override_settings(LANGUAGE_CODE="en")
def test_reader_creation_redirects_and_shows_token_once(client, management):
    # PRG: the POST redirects (refresh never re-submits) and the one-time
    # credential is popped from the session, so it renders exactly once.
    client.force_login(management.user)
    with patch("lamto.accounts.middleware.require_staff_mfa"), patch("lamto.web.staff.require_staff_mfa"), patch("lamto.web.views.gate.require_recent_auth"):
        response = client.post(reverse("web:gate-devices"), {"action": "create", "label": "North", "direction": GateDevice.Direction.ENTRY}, follow=True)
        second = client.get(reverse("web:gate-devices"))

    assert response.redirect_chain == [(reverse("web:gate-devices"), 302)]
    html = response.content.decode()
    assert "This credential is shown once" in html
    assert "data-copy=" in html
    assert "This credential is shown once" not in second.content.decode()
