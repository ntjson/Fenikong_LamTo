from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from lamto.accounts.models import (
    Building,
    ManagementMembership,
    ResidentOccupancy,
    Unit,
    User,
)
from lamto.audit.models import AuditEvent
from lamto.notifications.announcements import (
    AnnouncementConflict,
    edit_announcement,
    publish_announcement,
    withdraw_announcement,
)
from lamto.notifications.models import (
    Announcement,
    Device,
    NotificationDelivery,
    NotificationPreference,
)
from lamto.notifications.services import process_due_notifications


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class AnnouncementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="Building One")
        cls.other_building = Building.objects.create(name="Building Two")
        cls.unit = Unit.objects.create(building=cls.building, label="101")
        cls.other_unit = Unit.objects.create(building=cls.other_building, label="201")
        cls.manager = User.objects.create_user(
            email="manager@example.test", password="pw", display_name="Manager"
        )
        cls.membership = ManagementMembership.objects.create(
            user=cls.manager, building=cls.building
        )

    def test_model_defaults_and_length_validation(self):
        announcement = Announcement(
            building=self.building,
            title="Notice",
            body="Details",
            created_by=self.manager,
            updated_by=self.manager,
        )

        assert announcement.revision == 1
        assert announcement.state == Announcement.State.PUBLISHED

        announcement.title = "x" * 161
        announcement.body = "x" * 2001
        with self.assertRaises(ValidationError) as error:
            announcement.full_clean()
        assert set(error.exception.message_dict) == {"title", "body"}

    def test_publish_requires_active_management_of_selected_building(self):
        with self.assertRaises(PermissionDenied):
            publish_announcement(
                self.manager, self.other_building.id, "Notice", "Details"
            )

        self.membership.active = False
        self.membership.save(update_fields=["active"])
        with self.assertRaises(PermissionDenied):
            publish_announcement(self.manager, self.building.id, "Notice", "Details")

        assert not Announcement.objects.exists()

    def test_publish_fans_out_once_to_each_distinct_active_resident(self):
        resident = User.objects.create_user(
            email="resident@example.test", password="pw", display_name="Resident"
        )
        second_unit = Unit.objects.create(building=self.building, label="102")
        ResidentOccupancy.objects.create(user=resident, unit=self.unit)
        ResidentOccupancy.objects.create(user=resident, unit=second_unit)

        inactive_occupancy = User.objects.create_user(
            email="inactive-occupancy@example.test",
            password="pw",
            display_name="Inactive occupancy",
        )
        ResidentOccupancy.objects.create(
            user=inactive_occupancy, unit=self.unit, active=False
        )
        inactive_user = User.objects.create_user(
            email="inactive-user@example.test",
            password="pw",
            display_name="Inactive user",
            is_active=False,
        )
        ResidentOccupancy.objects.create(user=inactive_user, unit=self.unit)
        other_resident = User.objects.create_user(
            email="other@example.test", password="pw", display_name="Other"
        )
        ResidentOccupancy.objects.create(user=other_resident, unit=self.other_unit)

        announcement = publish_announcement(
            self.manager, self.building.id, "Water shutdown", "From 10:00 to 12:00"
        )

        delivery = NotificationDelivery.objects.get(
            recipient=resident,
            channel=NotificationDelivery.Channel.IN_APP,
        )
        assert delivery.event_key == (
            f"building.announcement:announcement:{announcement.id}"
        )
        assert delivery.event_code == "building.announcement"
        assert delivery.subject == announcement.title
        assert delivery.body == announcement.body
        assert delivery.status == NotificationDelivery.Status.AVAILABLE
        process_due_notifications(limit=10)
        assert NotificationDelivery.objects.count() == 1
        assert not NotificationDelivery.objects.filter(
            channel=NotificationDelivery.Channel.EMAIL
        ).exists()

        event = AuditEvent.objects.get(action="announcement.published")
        assert event.actor == self.manager
        assert event.membership == self.membership
        assert event.membership.building == self.building
        assert event.result == "accepted"
        assert event.target_type == "Announcement"
        assert event.target_id == str(announcement.id)
        assert event.metadata == {
            "announcement_id": announcement.id,
            "revision": 1,
        }
        assert "title" not in event.metadata
        assert "body" not in event.metadata

    @override_settings(PUSH_ENABLED=True)
    def test_publish_push_is_preference_gated_and_never_emails(self):
        enabled = User.objects.create_user(
            email="enabled@example.test", password="pw", display_name="Enabled"
        )
        disabled = User.objects.create_user(
            email="disabled@example.test", password="pw", display_name="Disabled"
        )
        for index, resident in enumerate((enabled, disabled), 1):
            ResidentOccupancy.objects.create(user=resident, unit=self.unit)
            Device.objects.create(
                user=resident,
                install_id=f"install-{index}",
                fcm_token=f"token-{index}",
                platform=Device.Platform.ANDROID,
                last_seen_at=timezone.now(),
            )
        NotificationPreference.objects.create(
            user=disabled,
            event_code="building.announcement",
            email_enabled=True,
            push_enabled=False,
        )

        announcement = publish_announcement(
            self.manager, self.building.id, "Private title", "Private body"
        )

        assert NotificationDelivery.objects.filter(
            channel=NotificationDelivery.Channel.IN_APP
        ).count() == 2
        push = NotificationDelivery.objects.get(
            recipient=enabled, channel=NotificationDelivery.Channel.PUSH
        )
        assert push.event_key.endswith(
            f"announcement:{announcement.id}:revision:1:published"
        )
        assert not NotificationDelivery.objects.filter(
            recipient=disabled, channel=NotificationDelivery.Channel.PUSH
        ).exists()
        assert not NotificationDelivery.objects.filter(
            channel=NotificationDelivery.Channel.EMAIL
        ).exists()

    @override_settings(PUSH_ENABLED=True)
    def test_edit_and_withdraw_are_revision_locked_and_terminal(self):
        resident = User.objects.create_user(
            email="resident-lifecycle@example.test",
            password="pw",
            display_name="Resident",
        )
        ResidentOccupancy.objects.create(user=resident, unit=self.unit)
        Device.objects.create(
            user=resident,
            install_id="lifecycle-install",
            fcm_token="lifecycle-token",
            platform=Device.Platform.ANDROID,
            last_seen_at=timezone.now(),
        )
        announcement = publish_announcement(
            self.manager, self.building.id, "Original", "Original body"
        )
        process_due_notifications(limit=10)
        inbox = NotificationDelivery.objects.get(
            recipient=resident, channel=NotificationDelivery.Channel.IN_APP
        )
        inbox.read_at = timezone.now()
        inbox.save(update_fields=["read_at"])

        newcomer = User.objects.create_user(
            email="newcomer@example.test", password="pw", display_name="Newcomer"
        )
        ResidentOccupancy.objects.create(user=newcomer, unit=self.unit)
        Device.objects.create(
            user=newcomer,
            install_id="newcomer-install",
            fcm_token="newcomer-token",
            platform=Device.Platform.IOS,
            last_seen_at=timezone.now(),
        )

        edited = edit_announcement(
            self.manager,
            announcement.id,
            expected_revision=1,
            title="Updated",
            body="Updated body",
        )
        assert edited.revision == 2
        assert edited.updated_by == self.manager
        inbox_rows = NotificationDelivery.objects.filter(
            channel=NotificationDelivery.Channel.IN_APP,
            event_key=f"building.announcement:announcement:{announcement.id}",
        )
        assert inbox_rows.count() == 2
        assert not inbox_rows.exclude(
            subject="Updated",
            body="Updated body",
            read_at=None,
            status=NotificationDelivery.Status.AVAILABLE,
        ).exists()
        assert NotificationDelivery.objects.filter(
            channel=NotificationDelivery.Channel.PUSH,
            event_key__endswith=f"announcement:{announcement.id}:revision:2:updated",
        ).count() == 2

        with self.assertRaises(AnnouncementConflict):
            edit_announcement(
                self.manager,
                announcement.id,
                expected_revision=1,
                title="Duplicate",
                body="Duplicate body",
            )
        assert NotificationDelivery.objects.filter(
            channel=NotificationDelivery.Channel.PUSH,
            event_key__contains=f"announcement:{announcement.id}:revision:2:updated",
        ).count() == 2

        withdrawn = withdraw_announcement(
            self.manager, announcement.id, expected_revision=2
        )
        assert withdrawn.revision == 3
        assert withdrawn.state == Announcement.State.WITHDRAWN
        assert withdrawn.withdrawn_at is not None
        assert not inbox_rows.exists()
        assert NotificationDelivery.objects.filter(
            channel=NotificationDelivery.Channel.PUSH,
            event_key__endswith=f"announcement:{announcement.id}:revision:3:withdrawn",
        ).count() == 2
        assert AuditEvent.objects.filter(action="announcement.updated").count() == 1
        assert AuditEvent.objects.filter(action="announcement.withdrawn").count() == 1

        with self.assertRaises(AnnouncementConflict):
            edit_announcement(
                self.manager,
                announcement.id,
                expected_revision=3,
                title="Too late",
                body="Too late",
            )
        with self.assertRaises(AnnouncementConflict):
            withdraw_announcement(
                self.manager, announcement.id, expected_revision=3
            )

    def test_manager_from_another_building_cannot_mutate_announcement(self):
        other_manager = User.objects.create_user(
            email="other-manager@example.test",
            password="pw",
            display_name="Other manager",
        )
        ManagementMembership.objects.create(
            user=other_manager, building=self.other_building
        )
        announcement = publish_announcement(
            self.manager, self.building.id, "Original", "Original body"
        )

        with self.assertRaises(PermissionDenied):
            edit_announcement(
                other_manager,
                announcement.id,
                expected_revision=1,
                title="Unauthorized",
                body="Unauthorized",
            )
        with self.assertRaises(PermissionDenied):
            withdraw_announcement(
                other_manager, announcement.id, expected_revision=1
            )
