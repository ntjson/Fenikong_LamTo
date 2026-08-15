
import pytest
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone
from knox.models import AuthToken

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.audit.models import AuditEvent
from lamto.notifications.announcements import edit_announcement, publish_announcement
from lamto.notifications.models import (
    Announcement,
    Device,
    NotificationDelivery,
    NotificationPreference,
)
from lamto.notifications.push import build_push_payload
from lamto.notifications.services import process_due_notifications


pytestmark = pytest.mark.django_db


def setup_manager(client, name="Tower A", email="manager@example.test"):
    building = Building.objects.create(name=name)
    manager = User.objects.create_user(email=email, password="secret")
    ManagementMembership.objects.create(user=manager, building=building)
    client.force_login(manager)
    return building, manager


def test_history_is_building_scoped_newest_first_with_audit_fields(client):
    building, manager = setup_manager(client)
    older = publish_announcement(manager, building.pk, "Older", "First")
    newer = publish_announcement(manager, building.pk, "Newer", "Second")
    newer.state = Announcement.State.WITHDRAWN
    newer.revision = 2
    newer.save()
    other_building = Building.objects.create(name="Tower B")
    ManagementMembership.objects.create(user=manager, building=other_building)
    publish_announcement(manager, other_building.pk, "Other", "Hidden")

    response = client.get(reverse("web:staff-announcement-list"))

    assert list(response.context["announcements"]) == [newer, older]
    content = response.content.decode()
    assert manager.email in content
    assert "Revision 2" in content or "Phiên bản 2" in content
    # State labels are translated under LANGUAGE_CODE=vi.
    assert "Withdrawn" in content or "Đã rút" in content
    assert "Published" in content or "Đã công bố" in content
    assert b"Other" not in response.content
    assert older.created_at.strftime("%Y").encode() in response.content


def test_publish_strips_whitespace_and_enforces_limits(client):
    building, _manager = setup_manager(client)

    response = client.post(
        reverse("web:staff-announcement-create"),
        {"title": "  Water notice  ", "body": "  Starts tonight.  "},
    )

    announcement = Announcement.objects.get()
    assert response.status_code == 302
    assert announcement.building == building
    assert (announcement.title, announcement.body) == (
        "Water notice",
        "Starts tonight.",
    )

    response = client.post(
        reverse("web:staff-announcement-create"),
        {"title": "x" * 161, "body": "y" * 2001},
    )
    assert response.status_code == 200
    assert Announcement.objects.count() == 1
    assert response.context["form"].errors.keys() == {"title", "body"}


@pytest.mark.parametrize("data", [{"title": " ", "body": "Body"}, {"title": "Title", "body": " "}])
def test_blank_publish_redisplays_errors_without_side_effects(client, data):
    setup_manager(client)

    response = client.post(reverse("web:staff-announcement-create"), data)

    assert response.status_code == 200
    assert response.context["form"].errors
    assert not Announcement.objects.exists()
    assert not NotificationDelivery.objects.exists()


@pytest.mark.parametrize("route", ["detail", "edit", "withdraw"])
def test_cross_building_announcement_routes_return_404(client, route):
    _building, manager = setup_manager(client)
    other = Building.objects.create(name="Tower B")
    ManagementMembership.objects.create(user=manager, building=other)
    announcement = publish_announcement(manager, other.pk, "Other", "Hidden")
    url = reverse(f"web:staff-announcement-{route}", args=[announcement.pk])

    response = client.post(url, {"expected_revision": 1}) if route == "withdraw" else client.get(url)

    assert response.status_code == 404


def test_stale_edit_reports_conflict_and_preserves_newer_content(client):
    building, manager = setup_manager(client)
    announcement = publish_announcement(manager, building.pk, "Original", "Body")
    edit_url = reverse("web:staff-announcement-edit", args=[announcement.pk])
    assert client.get(edit_url).context["form"]["expected_revision"].value() == 1
    edit_announcement(
        manager,
        announcement.pk,
        expected_revision=1,
        title="Newer",
        body="Current body",
    )

    response = client.post(
        edit_url,
        {"title": "Stale", "body": "Old body", "expected_revision": 1},
        follow=True,
    )

    announcement.refresh_from_db()
    assert (announcement.title, announcement.body, announcement.revision) == (
        "Newer",
        "Current body",
        2,
    )
    body = response.content.decode()
    assert "changed since you opened it" in body or "đã thay đổi kể từ khi bạn mở" in body


def test_withdraw_requires_post_and_csrf(client):
    building, manager = setup_manager(client)
    announcement = publish_announcement(manager, building.pk, "Notice", "Body")
    url = reverse("web:staff-announcement-withdraw", args=[announcement.pk])

    assert client.get(url).status_code == 405
    announcement.refresh_from_db()
    assert announcement.state == Announcement.State.PUBLISHED

    client.handler.enforce_csrf_checks = True
    assert client.post(url, {"expected_revision": 1}).status_code == 403
    announcement.refresh_from_db()
    assert announcement.state == Announcement.State.PUBLISHED


def test_withdrawn_detail_has_no_actions_and_remains_in_history(client):
    building, manager = setup_manager(client)
    announcement = publish_announcement(manager, building.pk, "Notice", "Body")
    response = client.post(
        reverse("web:staff-announcement-withdraw", args=[announcement.pk]),
        {"expected_revision": 1},
    )
    announcement.refresh_from_db()

    assert response.status_code == 302
    assert announcement.state == Announcement.State.WITHDRAWN
    detail = client.get(reverse("web:staff-announcement-detail", args=[announcement.pk]))
    assert b"Edit announcement" not in detail.content
    assert b"Withdraw announcement" not in detail.content
    history = client.get(reverse("web:staff-announcement-list"))
    assert announcement in history.context["announcements"]


@override_settings(PUSH_ENABLED=True)
def test_announcement_management_to_resident_api_lifecycle(client, monkeypatch):
    monkeypatch.setattr(
        "lamto.notifications.services.send_push",
        lambda *args, **kwargs: "msg-test",
    )
    building, manager = setup_manager(client)
    unit = Unit.objects.create(building=building, label="101")
    second_unit = Unit.objects.create(building=building, label="102")
    enabled = User.objects.create_user(email="enabled@example.test", password="pw")
    disabled = User.objects.create_user(email="disabled@example.test", password="pw")
    ResidentOccupancy.objects.create(user=enabled, unit=unit)
    ResidentOccupancy.objects.create(user=enabled, unit=second_unit)
    ResidentOccupancy.objects.create(user=disabled, unit=unit)
    for index, resident in enumerate((enabled, disabled), 1):
        Device.objects.create(
            user=resident,
            install_id=f"lifecycle-{index}",
            fcm_token=f"token-{index}",
            platform=Device.Platform.ANDROID,
            last_seen_at=timezone.now(),
        )
    NotificationPreference.objects.create(
        user=disabled,
        event_code="building.announcement",
        push_enabled=False,
    )

    response = client.post(
        reverse("web:staff-announcement-create"),
        {"title": "Water shutdown", "body": "From 10:00 to 12:00"},
    )
    announcement = Announcement.objects.get()
    assert response.status_code == 302
    in_app_key = f"building.announcement:announcement:{announcement.pk}"
    assert NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.IN_APP, event_key=in_app_key
    ).count() == 2
    published_push = NotificationDelivery.objects.get(
        channel=NotificationDelivery.Channel.PUSH,
        event_key__endswith=f"announcement:{announcement.pk}:revision:1:published",
    )
    assert published_push.recipient_id == enabled.pk
    push_title, push_body, _data = build_push_payload(published_push)
    assert announcement.title not in push_title + push_body
    assert announcement.body not in push_title + push_body

    process_due_notifications(limit=10)
    api_client = Client()
    _token, token = AuthToken.objects.create(user=enabled)
    auth = {"authorization": f"Token {token}"}
    occupancy = ResidentOccupancy.objects.filter(user=enabled).first()
    feed = api_client.get(
        reverse("api:notifications"),
        {"event_code": "building.announcement", "unread": "true"},
        headers={**auth, "x-lamto-occupancy": str(occupancy.pk)},
    )
    row = feed.json()["results"][0]
    assert (feed.status_code, row["subject"], row["body"]) == (
        200,
        "Water shutdown",
        "From 10:00 to 12:00",
    )
    assert api_client.post(
        reverse("api:notification-read", kwargs={"pk": row["id"]}), headers=auth
    ).status_code == 204

    newcomer = User.objects.create_user(email="newcomer@example.test", password="pw")
    ResidentOccupancy.objects.create(user=newcomer, unit=unit)
    Device.objects.create(
        user=newcomer,
        install_id="lifecycle-newcomer",
        fcm_token="newcomer-token",
        platform=Device.Platform.IOS,
        last_seen_at=timezone.now(),
    )
    edit = client.post(
        reverse("web:staff-announcement-edit", args=[announcement.pk]),
        {"title": "Updated", "body": "Updated body", "expected_revision": 1},
    )
    assert edit.status_code == 302
    inbox = NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.IN_APP, event_key=in_app_key
    )
    assert inbox.count() == 3
    assert not inbox.exclude(subject="Updated", body="Updated body", read_at=None).exists()
    updated_pushes = NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.PUSH,
        event_key__endswith=f"announcement:{announcement.pk}:revision:2:updated",
    )
    assert set(updated_pushes.values_list("recipient_id", flat=True)) == {
        enabled.pk,
        newcomer.pk,
    }
    for updated_push in updated_pushes:
        push_title, push_body, _data = build_push_payload(updated_push)
        assert "Updated" not in push_title + push_body
        assert "Updated body" not in push_title + push_body

    withdraw_url = reverse("web:staff-announcement-withdraw", args=[announcement.pk])
    stale = client.post(withdraw_url, {"expected_revision": 1}, follow=True)
    announcement.refresh_from_db()
    assert announcement.state == Announcement.State.PUBLISHED
    stale_body = stale.content.decode()
    assert (
        "changed since you opened it" in stale_body
        or "đã thay đổi kể từ khi bạn mở" in stale_body
    )

    assert client.post(withdraw_url, {"expected_revision": 2}).status_code == 302
    announcement.refresh_from_db()
    assert (announcement.state, announcement.revision) == (
        Announcement.State.WITHDRAWN,
        3,
    )
    assert not inbox.exists()
    withdrawn_push = NotificationDelivery.objects.filter(
        channel=NotificationDelivery.Channel.PUSH,
        event_key__endswith=f"announcement:{announcement.pk}:revision:3:withdrawn",
    ).first()
    assert withdrawn_push is not None
    push_title, push_body, _data = build_push_payload(withdrawn_push)
    assert announcement.title not in push_title + push_body
    assert announcement.body not in push_title + push_body
    assert not NotificationDelivery.objects.filter(
        event_code="building.announcement",
        channel=NotificationDelivery.Channel.EMAIL,
    ).exists()
    assert announcement in client.get(
        reverse("web:staff-announcement-list")
    ).context["announcements"]

    membership = ManagementMembership.objects.get(user=manager, building=building)
    events = AuditEvent.objects.filter(
        target_type="Announcement", target_id=str(announcement.pk)
    ).order_by("id")
    assert [event.action for event in events] == [
        "announcement.published",
        "announcement.updated",
        "announcement.withdrawn",
    ]
    for event, revision in zip(events, (1, 2, 3), strict=True):
        assert event.actor == manager
        assert event.membership == membership
        assert event.membership.building == building
        assert event.target_type == "Announcement"
        assert event.target_id == str(announcement.pk)
        assert event.result == "accepted"
        assert event.metadata == {
            "announcement_id": announcement.pk,
            "revision": revision,
        }
