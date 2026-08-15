from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from lamto.accounts.models import Building, ManagementMembership, ResidentOccupancy, Unit, User
from lamto.maintenance.cases import decline_report, reply_information, request_information
from lamto.maintenance.models import BuildingLocation, IssueReport


class OutcomeABTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="B1")
        cls.unit = Unit.objects.create(building=cls.building, label="A-101")
        cls.location = BuildingLocation.objects.create(building=cls.building, name="Lobby")
        cls.resident = User.objects.create_user(email="r@x.vn", password="pw", display_name="R")
        ResidentOccupancy.objects.create(user=cls.resident, unit=cls.unit)
        cls.manager = User.objects.create_user(email="m@x.vn", password="pw", display_name="M")
        ManagementMembership.objects.create(user=cls.manager, building=cls.building)

    def _report(self):
        return IssueReport.objects.create(
            reporter=self.resident, unit=self.unit, text="Leak",
            selected_location=self.location, location_path_snapshot="B1 / Lobby",
            status=IssueReport.Status.IN_REVIEW,
        )

    def test_info_loop_roundtrip(self):
        report = self._report()
        info = request_information(report, self.manager, "Which tap?")
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.NEEDS_INFO)
        reply_information(self.resident, report, "Kitchen tap")
        report.refresh_from_db()
        info.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.IN_REVIEW)
        self.assertEqual(info.reply_text, "Kitchen tap")
        self.assertIsNotNone(info.resolved_at)

    def test_second_open_info_request_rejected(self):
        report = self._report()
        request_information(report, self.manager, "Which tap?")
        with self.assertRaises(ValidationError):
            request_information(report, self.manager, "And which floor?")

    def test_reply_requires_reporter(self):
        report = self._report()
        request_information(report, self.manager, "Which tap?")
        stranger = User.objects.create_user(email="s@x.vn", password="pw", display_name="S")
        with self.assertRaises(PermissionDenied):
            reply_information(stranger, report, "hi")

    def test_decline_records_reason_and_notifies_state(self):
        report = self._report()
        decline_report(report, self.manager, "Duplicate of an already fixed issue")
        report.refresh_from_db()
        self.assertEqual(report.status, IssueReport.Status.DECLINED)
        self.assertEqual(report.declined_reason, "Duplicate of an already fixed issue")
        self.assertEqual(report.declined_by_id, self.manager.pk)
        self.assertIsNotNone(report.declined_at)

    def test_decline_requires_reason_and_management(self):
        report = self._report()
        with self.assertRaises(ValidationError):
            decline_report(report, self.manager, "   ")
        with self.assertRaises(PermissionDenied):
            decline_report(report, self.resident, "reason")

    def test_terminal_report_cannot_get_info_request(self):
        report = self._report()
        decline_report(report, self.manager, "No.")
        with self.assertRaises(ValidationError):
            request_information(report, self.manager, "Too late?")
