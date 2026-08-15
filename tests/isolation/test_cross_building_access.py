"""Two-building adversarial isolation suite (spec 2.3 layer 4).

Building A actors request Building B objects by primary key: the answer must
always be 404 (cross-tenant), 403 (ownership), or 405 (method), never data.
List pages and exports rendered for Building A must not contain Building B
markers.

Completeness:
- Web: every <int:pk> route must appear in STAFF_CASES, RESIDENT_CASES, or EXEMPT.
- API: every registered named route must appear in exactly one of the API
  classification maps (clarification 4: public-auth / authenticated-global /
  tenant-list / tenant-object / explicitly exempt).
"""

import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse
from knox.models import AuthToken

from lamto.accounts.models import ResidentOccupancy
from lamto.accounts.registration import submit_registration
from lamto.billing.models import Bill
from lamto.documents.models import Document, DocumentVersion, QuarantinedUpload
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.finance.fund import fund_balance
from lamto.finance.models import (
    MaintenanceFundEntry,
    Settlement,
    Proposal,
    PublishedLedgerEntry,
)
from lamto.gate.models import FaceEnrollment, PendingEnrollmentPhoto, VehiclePlate
from lamto.maintenance.models import BuildingLocation, IssueReport, MaintenanceCase
from lamto.notifications.models import NotificationDelivery
from lamto.notifications.announcements import publish_announcement
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world
from lamto.web.staff import nav_items_for

_TEMP_STORAGE = tempfile.mkdtemp(prefix="lamto-isolation-")

B_BUILDING_NAME = "Isolation Building B"
B_LEAK_MARKER = "TEST-B-LEAK-MARKER"

# route name -> (attribute on cls.b with the B-side pk, method)
STAFF_CASES = {
    "web:staff-report-detail": ("report_pk", "GET"),
    "web:case-detail": ("case_pk", "GET"),
    "web:proposal-detail": ("proposal_pk", "GET"),
    "web:proposal-create": ("case_pk", "POST"),
    "web:settlement-record-transfer": ("proposal_pk", "POST"),
    "web:settlement-record-ack": ("settlement_pk", "POST"),
    "web:settlement-detail": ("settlement_pk", "GET"),
    "web:fund-verify": ("fund_entry_pk", "POST"),
    "web:gate-face-photo": ("face_pk", "GET"),
    "web:gate-face-decide": ("face_pk", "POST"),
    "web:gate-plate-decide": ("plate_pk", "POST"),
    "web:staff-registration-detail": ("registration_pk", "GET"),
    "web:staff-registration-approve": ("registration_pk", "POST"),
    "web:staff-registration-reject": ("registration_pk", "POST"),
    "web:staff-announcement-detail": ("announcement_pk", "GET"),
    "web:staff-announcement-edit": ("announcement_pk", "GET"),
    "web:staff-announcement-withdraw": ("announcement_pk", "POST"),
    "web:staff-bill-detail": ("bill_pk", "GET"),
    "web:staff-bill-void": ("bill_pk", "POST"),
    "web:staff-document": ("document_version_pk", "GET"),
    # Third element (optional): URL args placed before the pk.
    "web:exception-review": ("ledger_pk", "GET", ("integrity_mismatch",)),
}
STAFF_FORBIDDEN_CASES = set()

RESIDENT_CASES = {}

EXEMPT = {}

LIST_ROUTES = [
    "web:action-inbox",
    "web:case-list",
    "web:proposal-list",
    "web:settlement-list",
    "web:audit-export",
    "web:exception-list",
]

# ---------------------------------------------------------------------------
# API route classification (clarification 4). Completeness walks *every*
# named pattern in lamto.api.urls — not only <int:pk> routes.
# ---------------------------------------------------------------------------

# Public unauthenticated auth surface (login).
API_PUBLIC_AUTH = {
    "api:auth-login": "POST login (phone/email → knox token)",
    "api:registration-options": "GET public building/unit options",
    "api:registration-create": "POST public registration request",
    "api:registration-status": "GET status by registration secret",
}

# Authenticated but user-scoped, not building-tenant.
API_AUTHENTICATED_GLOBAL = {
    "api:auth-logout": "POST revoke current knox token",
    "api:auth-logout-all": "POST revoke all knox tokens for user",
    "api:me": "GET profile + occupancies",
    "api:me-notification-preferences": "PATCH email/push notification preferences",
    "api:devices": "POST register/upsert FCM device",
    "api:device-delete": "DELETE deactivate this install's device",
}

# Tenant-scoped lists / aggregates (building via occupancy resolution).
API_TENANT_LIST = {
    "api:proposal-list": "GET",
    "api:ledger-list": "GET",
    "api:fund-summary": "GET",
    "api:fund-series": "GET",
    "api:locations": "GET",
    "api:notifications": "GET",
    "api:gate-registrations": "GET",
}

# Tenant-scoped object access by primary key.
# route -> (attribute on cls.b with the B-side pk, method, expected status)
API_TENANT_OBJECT = {
    "api:proposal-detail": ("proposal_pk", "GET", 404),
    "api:proposal-rating": ("proposal_pk", "POST", 404),
    "api:ledger-detail": ("ledger_pk", "GET", 404),
    "api:report-detail": ("report_pk", "GET", 404),
    "api:report-photos": ("report_pk", "POST", 404),
    "api:report-info-reply": ("report_pk", "POST", 404),
    "api:case-rating": ("case_pk", "POST", 404),
    "api:notification-read": ("notification_pk", "POST", 404),
    "api:gate-plate-detail": ("plate_pk", "DELETE", 404),
    "api:bills-detail": ("bill_pk", "GET", 404),
    "api:bills-confirm-payment": ("bill_pk", "POST", 404),
}

# Ownership-scoped lists/writes (the caller's own rows; never building-tenant).
API_OWNERSHIP_LIST = {
    "api:reports": "GET mine + POST create",
    "api:gate-plates": "POST plate for current occupancy",
    "api:gate-face": "POST/DELETE face for current occupancy",
    "api:bills-list": "GET own bills",
}

# Explicitly non-tenant / non-walked routes (none in Phase 0).
API_EXEMPT = {
    "api:document-download": "signed-token download; authorization re-runs at redemption (see test_downloads)",
    "api:gate-device": "gate-device credential is building-scoped",
    "api:gate-recognize-face": "gate-device credential is building-scoped",
    "api:gate-recognize-plate": "gate-device credential is building-scoped",
}

# Back-compat aliases used by walk helpers (brief Step 1 names).
API_RESIDENT_CASES = API_TENANT_OBJECT
API_LIST_ROUTES = list(API_TENANT_LIST)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP_STORAGE},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class CrossBuildingAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seed_a = seed_pilot_world(
            building_name="Isolation Building A",
            email_prefix="isoa",
            create_sample_report=True,
        )
        cls.seed_b = seed_pilot_world(
            building_name=B_BUILDING_NAME,
            email_prefix="isob",
            create_sample_report=False,
        )
        driver = PilotDomainDriver(cls.seed_b)
        driver.submit_report(f"{B_LEAK_MARKER} lift noise", "Lift 2")
        driver.confirm_triage_case()
        driver.publish_proposal()
        driver.complete_assigned_work()
        driver.record_settlement_transfer()
        driver.record_settlement_ack()
        driver.confirm_all_chain_events()
        driver.publish_settlement_entry()
        driver.confirm_all_chain_events()

        b_building = cls.seed_b.building
        report = IssueReport.objects.get(unit__building=b_building)
        case = MaintenanceCase.objects.get(building=b_building)
        proposal = Proposal.objects.get(case=case)
        settlement = Settlement.objects.get(proposal=proposal)

        ledger = PublishedLedgerEntry.objects.get(case=case)

        b_fund_entry = MaintenanceFundEntry.objects.get(
            fund__building=b_building,
            entry_type=MaintenanceFundEntry.EntryType.OPENING_BALANCE,
        )
        cls.b = {
            "report_pk": report.pk,
            "case_pk": case.pk,
            "proposal_pk": proposal.pk,
            "settlement_pk": settlement.pk,
            "settlement_pk": settlement.pk,
            "ledger_pk": ledger.pk,
            "fund_entry_pk": b_fund_entry.pk,
        }
        cls.b["outbox_event_pk"] = (
            BlockchainOutboxEvent.objects.filter(building=b_building)
            .values_list("pk", flat=True)
            .first()
        )
        cls.b["quarantine_pk"] = QuarantinedUpload.objects.create(
            uploader=cls.seed_b.management_memberships[0].user,
            building=b_building,
            filename=f"{B_LEAK_MARKER}.pdf",
            byte_size=1,
            reason="virus signature",
            retention_expires_at=timezone.now() + timedelta(days=1),
        ).pk
        b_notice = NotificationDelivery.objects.create(
            recipient=cls.seed_b.residents[0],
            building=b_building,
            channel=NotificationDelivery.Channel.IN_APP,
            status=NotificationDelivery.Status.AVAILABLE,
            event_key="ledger.publication:iso:1",
            event_code="ledger.publication",
            subject="B notice",
            body=B_LEAK_MARKER,
        )
        cls.b["notification_pk"] = b_notice.pk
        b_occupancy = ResidentOccupancy.objects.get(
            user=cls.seed_b.residents[0], active=True
        )
        face = FaceEnrollment.objects.create(occupancy=b_occupancy, embedding=b"sealed")
        PendingEnrollmentPhoto.objects.create(
            enrollment=face,
            storage_key="isolation/building-b-face.jpg",
            content_type="image/jpeg",
            byte_size=1,
            expires_at=timezone.now() + timedelta(days=1),
        )
        plate = VehiclePlate.objects.create(
            occupancy=b_occupancy,
            building=b_building,
            plate="51B12345",
        )
        cls.b.update(face_pk=face.pk, plate_pk=plate.pk)
        cls.b["registration_pk"] = submit_registration(
            full_name="Isolation Resident B",
            phone="0901234567",
            email="isolation-registration-b@example.test",
            password="correct horse battery staple",
            building_id=b_building.pk,
            unit_id=b_occupancy.unit_id,
        ).request.pk
        cls.b["announcement_pk"] = publish_announcement(
            cls.seed_b.management_memberships[0].user,
            b_building.pk,
            "Building B announcement",
            B_LEAK_MARKER,
        ).pk
        bill_document = Document.objects.create(
            building=b_building,
            kind=Document.Kind.RESIDENT_BILL,
        )
        bill_version = DocumentVersion.objects.create(
            document=bill_document,
            version=1,
            storage_key="isolation/building-b-bill.pdf",
            filename="bill.pdf",
            content_type="application/pdf",
            byte_size=1,
            sha256="0" * 64,
            uploader=cls.seed_b.management_memberships[0].user,
        )
        cls.b["document_version_pk"] = bill_version.pk
        cls.b["bill_pk"] = Bill.objects.create(
            building=b_building,
            resident=cls.seed_b.residents[0],
            title="Building B bill",
            amount_vnd=1000,
            document=bill_version,
            issued_by=cls.seed_b.management_memberships[0].user,
        ).pk

    def _management_login(self):
        membership = self.seed_a.management_memberships[0]
        user = membership.user
        self.client.force_login(user)

    def test_every_registered_route_is_classified(self):
        """Web <int:pk> routes + every registered API route must be classified."""
        from lamto.api import urls as api_urls
        from lamto.web import urls as web_urls

        pk_routes = {
            f"web:{pattern.name}"
            for pattern in web_urls.urlpatterns
            if "<int:" in str(pattern.pattern)
        }
        web_classified = set(STAFF_CASES) | set(RESIDENT_CASES) | set(EXEMPT)
        missing_web = pk_routes - web_classified
        assert not missing_web, (
            f"New web pk routes must be classified in the isolation suite: "
            f"{missing_web}"
        )

        # Clarification 4: every registered API route, not only <int:pk>.
        api_routes = {
            f"api:{pattern.name}"
            for pattern in api_urls.urlpatterns
            if getattr(pattern, "name", None)
        }
        api_classified = (
            set(API_PUBLIC_AUTH)
            | set(API_AUTHENTICATED_GLOBAL)
            | set(API_TENANT_LIST)
            | set(API_TENANT_OBJECT)
            | set(API_OWNERSHIP_LIST)
            | set(API_EXEMPT)
        )
        missing_api = api_routes - api_classified
        extra_api = api_classified - api_routes
        assert not missing_api, (
            f"New API routes must be classified in the isolation suite "
            f"(public-auth / authenticated-global / tenant-list / "
            f"tenant-object / ownership-list / explicitly exempt): {missing_api}"
        )
        assert not extra_api, (
            f"Isolation suite classifies unknown API routes: {extra_api}"
        )

        # Classification maps must be disjoint so a route has one category.
        maps = [
            set(API_PUBLIC_AUTH),
            set(API_AUTHENTICATED_GLOBAL),
            set(API_TENANT_LIST),
            set(API_TENANT_OBJECT),
            set(API_OWNERSHIP_LIST),
            set(API_EXEMPT),
        ]
        seen: set[str] = set()
        for bucket in maps:
            overlap = seen & bucket
            assert not overlap, f"API route classified more than once: {overlap}"
            seen |= bucket

    def test_management_has_five_areas_and_non_manager_is_denied(self):
        manager = self.seed_a.management_memberships[0]
        assert [item["active_key"] for item in nav_items_for(manager)] == [
            "inbox",
            "cases",
            "finance",
            "building",
            "ops",
        ]
        self._management_login()
        assert self.client.get(reverse("web:case-list")).status_code == 200
        assert self.client.get(reverse("web:audit-export")).status_code == 200
        self.client.logout()

        non_manager = get_user_model().objects.create_user(
            email="non-manager@isolation.test", password="x", display_name="Non-manager"
        )
        self.client.force_login(non_manager)
        assert self.client.get(reverse("web:case-list")).status_code == 403

    def test_staff_cannot_reach_other_building_objects(self):
        for route, case in STAFF_CASES.items():
            pk_attr, method, *prefix_args = case
            with self.subTest(route=route):
                self._management_login()
                url = reverse(
                    route,
                    args=[*(prefix_args[0] if prefix_args else ()), self.b[pk_attr]],
                )
                response = (
                    self.client.post(url, {})
                    if method == "POST"
                    else self.client.get(url)
                )
                # Object lookups hide other tenants with 404; service-layer
                # authorization may reject them with 403 before mutation.
                expected = 403 if route in STAFF_FORBIDDEN_CASES else 404
                assert response.status_code == expected, (route, response.status_code)
                if hasattr(response, "content"):
                    assert B_LEAK_MARKER.encode() not in response.content
                self.client.logout()

    def test_staff_cannot_reach_other_building_exceptions(self):
        """Every exception-review kind hides foreign-tenant objects with 404."""
        cases = [
            ("failed_outbox", self.b["outbox_event_pk"]),
            ("quarantined_upload", self.b["quarantine_pk"]),
        ]
        self._management_login()
        for kind, pk in cases:
            with self.subTest(kind=kind):
                response = self.client.get(
                    reverse("web:exception-review", args=[kind, pk])
                )
                assert response.status_code == 404, (kind, response.status_code)
                assert B_LEAK_MARKER.encode() not in response.content

    def test_resident_cannot_reach_other_building_objects(self):
        resident_a = self.seed_a.residents[0]
        self.client.force_login(resident_a)
        for route, (pk_attr, method, expected) in RESIDENT_CASES.items():
            with self.subTest(route=route):
                url = reverse(route, args=[self.b[pk_attr]])
                response = (
                    self.client.post(url, {})
                    if method == "POST"
                    else self.client.get(url)
                )
                assert response.status_code == expected, (route, response.status_code)

    def _api_auth(self, user):
        _instance, token = AuthToken.objects.create(user=user)
        return {"authorization": f"Token {token}"}

    def test_api_resident_cannot_reach_other_building_objects(self):
        """Cross-building tenant-object access is 404 with no leak markers."""
        auth = self._api_auth(self.seed_a.residents[0])
        for route, (pk_attr, method, expected) in API_TENANT_OBJECT.items():
            with self.subTest(route=route):
                url = reverse(route, args=[self.b[pk_attr]])
                response = (
                    self.client.delete(url, headers=auth)
                    if method == "DELETE"
                    else self.client.post(url, {}, headers=auth)
                    if method == "POST"
                    else self.client.get(url, headers=auth)
                )
                # Design §2.3: cross-tenant object access is 404, never data.
                assert response.status_code == expected, (route, response.status_code)
                assert B_LEAK_MARKER.encode() not in response.content
                assert B_BUILDING_NAME.encode() not in response.content

    def test_api_rejects_foreign_occupancy_header(self):
        """Foreign occupancy header must not resolve to another building's data."""
        auth = self._api_auth(self.seed_a.residents[0])
        b_occupancy = ResidentOccupancy.objects.get(
            user=self.seed_b.residents[0], active=True
        )
        for route in API_TENANT_LIST:
            with self.subTest(route=route):
                response = self.client.get(
                    reverse(route),
                    headers={**auth, "x-lamto-occupancy": str(b_occupancy.pk)},
                )
                assert response.status_code == 404, (route, response.status_code)
                assert B_LEAK_MARKER.encode() not in response.content
                assert B_BUILDING_NAME.encode() not in response.content

        # Tenant-object routes: foreign occupancy header must not leak B data.
        # Ownership-scoped writes (report-photos) 404 on foreign pk before upload;
        # occupancy-scoped GETs 404 via the occupancy resolver.
        for route, (pk_attr, method, _expected) in API_TENANT_OBJECT.items():
            with self.subTest(route=route, kind="tenant-object"):
                url = reverse(route, args=[self.b[pk_attr]])
                headers = {**auth, "x-lamto-occupancy": str(b_occupancy.pk)}
                response = (
                    self.client.delete(url, headers=headers)
                    if method == "DELETE"
                    else self.client.post(url, {}, headers=headers)
                    if method == "POST"
                    else self.client.get(url, headers=headers)
                )
                assert response.status_code == 404, (route, response.status_code)
                assert B_LEAK_MARKER.encode() not in response.content
                assert B_BUILDING_NAME.encode() not in response.content

    def test_api_lists_never_leak_other_building(self):
        """Tenant lists/aggregates for A omit Building B data and markers."""
        auth = self._api_auth(self.seed_a.residents[0])

        list_response = self.client.get(reverse("api:ledger-list"), headers=auth)
        assert list_response.status_code == 200
        listed_ids = [row["id"] for row in list_response.json()["results"]]
        assert self.b["ledger_pk"] not in listed_ids
        assert B_LEAK_MARKER.encode() not in list_response.content
        assert B_BUILDING_NAME.encode() not in list_response.content

        fund_response = self.client.get(reverse("api:fund-summary"), headers=auth)
        assert fund_response.status_code == 200
        expected_balance = fund_balance(self.seed_a.building.pk, verified_only=True)
        assert fund_response.json()["balance_vnd"] == expected_balance
        # Building B has a paid work-order path; its balance must not be returned.
        b_balance = fund_balance(self.seed_b.building.pk, verified_only=True)
        if b_balance != expected_balance:
            assert fund_response.json()["balance_vnd"] != b_balance
        assert B_LEAK_MARKER.encode() not in fund_response.content
        assert B_BUILDING_NAME.encode() not in fund_response.content

        locations_response = self.client.get(reverse("api:locations"), headers=auth)
        assert locations_response.status_code == 200
        assert B_LEAK_MARKER.encode() not in locations_response.content
        assert B_BUILDING_NAME.encode() not in locations_response.content
        location_ids = {row["id"] for row in locations_response.json()}
        b_location_ids = set(
            BuildingLocation.objects.filter(building=self.seed_b.building).values_list(
                "pk", flat=True
            )
        )
        assert location_ids.isdisjoint(b_location_ids)

        notifications_response = self.client.get(
            reverse("api:notifications"), headers=auth
        )
        assert notifications_response.status_code == 200
        assert B_LEAK_MARKER.encode() not in notifications_response.content
        assert B_BUILDING_NAME.encode() not in notifications_response.content
        notice_ids = {row["id"] for row in notifications_response.json()["results"]}
        assert self.b["notification_pk"] not in notice_ids

    def test_staff_lists_and_exports_never_leak_other_building(self):
        self._management_login()
        for route in LIST_ROUTES:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                assert response.status_code == 200
                self.assertNotContains(response, B_BUILDING_NAME)
                self.assertNotContains(response, B_LEAK_MARKER)

    def test_auditor_export_never_leaks_other_building(self):
        self._management_login()
        b_event_ids = list(
            BlockchainOutboxEvent.objects.filter(
                building_id=self.seed_b.building.pk
            ).values_list("event_id", flat=True)
        )
        for kind in ("fund_entries", "outbox", "audit_events", "documents"):
            with self.subTest(kind=kind):
                response = self.client.get(reverse("web:audit-export"), {"kind": kind})
                assert response.status_code == 200
                body = (
                    b"".join(response.streaming_content)
                    if getattr(response, "streaming", False)
                    else response.content
                )
                assert B_LEAK_MARKER.encode() not in body
                assert B_BUILDING_NAME.encode() not in body
                for event_id in b_event_ids:
                    assert event_id.encode() not in body

    def test_api_reports_never_leak_other_users(self):
        resident_a = self.seed_a.residents[0]
        _instance, token = AuthToken.objects.create(user=resident_a)
        auth = {"authorization": f"Token {token}"}
        listing = self.client.get(reverse("api:reports"), headers=auth)
        assert listing.status_code == 200, listing.content
        assert B_LEAK_MARKER.encode() not in listing.content
        # B's report id is 404 for A's resident.
        miss = self.client.get(
            reverse("api:report-detail", kwargs={"pk": self.b["report_pk"]}),
            headers=auth,
        )
        assert miss.status_code == 404

    def test_api_download_reauthorizes_across_tenants(self):
        from lamto.api.downloads import issue_download_token

        resident_a = self.seed_a.residents[0]
        resident_b = self.seed_b.residents[0]
        _instance, token_a = AuthToken.objects.create(user=resident_a)
        auth_a = {"authorization": f"Token {token_a}"}
        # A ledger document from B's published expenditure.
        entry_b = PublishedLedgerEntry.objects.get(case__building=self.seed_b.building)
        redacted = entry_b.settlement.transfer
        # A token bound to B's resident is not redeemable by A's resident.
        forged = issue_download_token(resident_b.pk, redacted.pk)
        assert (
            self.client.get(
                reverse("api:document-download", args=[forged]), headers=auth_a
            ).status_code
            == 404
        )
        # Even a token A could mint for that version fails resident_can_download
        # (wrong building).
        self_minted = issue_download_token(resident_a.pk, redacted.pk)
        assert (
            self.client.get(
                reverse("api:document-download", args=[self_minted]), headers=auth_a
            ).status_code
            == 404
        )
