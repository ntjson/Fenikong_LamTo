from django.db import IntegrityError
from django.test import TestCase

from lamto.accounts.models import Building, Unit, User
from lamto.maintenance.models import BuildingLocation, InfoRequest, IssueReport


def _report(**kwargs):
    building = Building.objects.create(name=kwargs.pop("bname", "B1"))
    unit = Unit.objects.create(building=building, label="A-101")
    location = BuildingLocation.objects.create(building=building, name="Lobby")
    reporter = User.objects.create_user(
        email=kwargs.pop("email", "r@x.vn"), password="pw", display_name="R"
    )
    return IssueReport.objects.create(
        reporter=reporter,
        unit=unit,
        text="Broken light",
        selected_location=location,
        location_path_snapshot="B1 / Lobby",
        **kwargs,
    )


class LifecycleModelTests(TestCase):
    def test_new_report_defaults(self):
        report = _report()
        self.assertEqual(report.status, IssueReport.Status.SUBMITTED)
        self.assertFalse(report.is_private)
        self.assertEqual(report.declined_reason, "")
        self.assertIsNone(report.declined_at)

    def test_status_values(self):
        self.assertEqual(
            set(IssueReport.Status.values),
            {"SUBMITTED", "IN_REVIEW", "NEEDS_INFO", "DECLINED",
             "IN_PROGRESS", "PROPOSED", "COMPLETED", "CLOSED"},
        )

    def test_one_open_info_request_per_report(self):
        report = _report()
        manager = User.objects.create_user(email="m@x.vn", password="pw", display_name="M")
        InfoRequest.objects.create(report=report, message="Which floor?", created_by=manager)
        with self.assertRaises(IntegrityError):
            InfoRequest.objects.create(report=report, message="Photo?", created_by=manager)
