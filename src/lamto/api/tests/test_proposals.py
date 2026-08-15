import tempfile
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from knox.models import AuthToken

from lamto.api.views import ProposalCursorPagination
from lamto.documents.models import Document
from lamto.evidence.models import EvidenceLevel
from django.core.exceptions import ValidationError

from lamto.finance.models import Proposal
from lamto.finance.proposals import (
    create_standalone_proposal,
    decide_proposal,
    publish_proposal_version,
)
from lamto.maintenance.cases import complete_proposal_work, publish_progress
from lamto.maintenance.ratings import rate_completed_proposal
from lamto.testing.factories import PilotDomainDriver, new_event_id, seed_pilot_world

_TEMP = tempfile.mkdtemp(prefix="lamto-api-proposals-")


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": _TEMP},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class ProposalApiTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="API Proposals",
            email_prefix="apiprop",
            create_sample_report=False,
        )
        self.resident = self.seed.residents[0]
        self.manager = self.seed.management_memberships[0]

    def _auth(self):
        _instance, token = AuthToken.objects.create(user=self.resident)
        return {"authorization": f"Token {token}"}

    def _standalone(self, purpose):
        proposal = create_standalone_proposal(self.seed.building, self.manager)
        original = self.seed.document(
            Document.Kind.QUOTATION, self.manager.user, purpose.lower().replace(" ", "-")
        )
        publish_proposal_version(
            proposal,
            self.manager,
            amount_vnd=2_500_000,
            contractor_name="Lift Co",
            fund_code="GENERAL",
            purpose=purpose,
            proposed_action="Replace controller",
            expected_schedule="Within 14 days",
            quotation_versions=[original],
            event_id=new_event_id(),
        )
        proposal.refresh_from_db()
        return proposal

    def test_list_is_cursor_paginated_and_uses_typed_proposal_rows(self):
        first = self._standalone("First proposal")
        self._standalone("Second proposal")

        with patch.object(ProposalCursorPagination, "page_size", 1):
            response = self.client.get(
                reverse("api:proposal-list"), headers=self._auth()
            )

        assert response.status_code == 200, response.content
        body = response.json()
        assert set(body) == {"next", "previous", "results"}
        assert body["next"] and "cursor=" in body["next"]
        assert len(body["results"]) == 1
        row = body["results"][0]
        assert row["id"] != first.pk
        assert row["purpose"] == "Second proposal"
        assert row["amount_vnd"] == 2_500_000
        with patch.object(ProposalCursorPagination, "page_size", 1):
            second_page = self.client.get(body["next"], headers=self._auth())
        assert second_page.status_code == 200
        assert second_page.json()["results"][0]["id"] == first.pk

    def test_case_backed_detail_has_versions_documents_and_case_progress(self):
        driver = PilotDomainDriver(self.seed)
        driver.submit_report("Lift controller fails", "Lift 2")
        driver.confirm_triage_case()
        driver.publish_proposal()
        driver.complete_assigned_work()
        proposal = self.seed.proposal

        response = self.client.get(
            reverse("api:proposal-detail", args=[proposal.pk]), headers=self._auth()
        )

        assert response.status_code == 200, response.content
        body = response.json()
        assert body["purpose"] == "Thang máy"
        assert body["proposed_action"] == "Repair the affected equipment"
        assert body["amount_vnd"] > 0
        assert body["fund_code"] == "GENERAL"
        assert body["contractor_name"] == "Pilot Contractor Co"
        assert body["expected_schedule"] == "Within 14 days"
        assert body["versions"][0]["number"] == 1
        assert body["versions"][0]["published_at"]
        assert body["versions"][0]["evidence_level"] in {
            EvidenceLevel.PENDING,
            EvidenceLevel.LOCAL_SIGNED,
            EvidenceLevel.CHAIN_CONFIRMED,
        }
        document = body["versions"][0]["supporting_documents"][0]
        assert document["filename"].endswith(".pdf")
        assert self.client.get(
            document["download_url"], headers=self._auth()
        ).status_code == 200
        assert body["progress"][0]["cause"] == "Worn cable"
        assert body["progress"][0]["result"] == "Cable secured"
        assert body["settlement"] is None
        assert body["can_rate"] is False

    def test_standalone_detail_distinguishes_absent_pending_and_settled_payment(self):
        proposal = self._standalone("Preventive lift maintenance")
        decide_proposal(proposal, self.seed.management_users[0], True, "Go")
        publish_progress(
            proposal=proposal,
            manager=self.manager.user,
            cause="Scheduled maintenance",
            result="Work underway",
        )
        complete_proposal_work(
            proposal,
            self.manager.user,
            "Scheduled maintenance",
            "Work completed",
        )
        detail_url = reverse("api:proposal-detail", args=[proposal.pk])
        auth = self._auth()

        proposal.refresh_from_db()
        completed_at = proposal.completed_at
        proposal.completed_at = None
        proposal.save(update_fields=["completed_at"])
        malformed = self.client.get(detail_url, headers=auth).json()
        assert malformed["can_rate"] is False
        proposal.completed_at = completed_at
        proposal.save(update_fields=["completed_at"])
        assert self.client.get(detail_url, headers=auth).json()["can_rate"] is True
        proposal.status = Proposal.Status.CLOSED
        proposal.save(update_fields=["status"])
        assert self.client.get(detail_url, headers=auth).json()["can_rate"] is False
        proposal.status = Proposal.Status.COMPLETED
        proposal.save(update_fields=["status"])

        absent = self.client.get(detail_url, headers=auth).json()
        assert absent["progress"][0]["result"] == "Work underway"
        assert absent["settlement"] is None
        assert absent["can_rate"] is True

        driver = PilotDomainDriver(self.seed)
        driver._ctx.update(proposal=proposal, amount_vnd=2_500_000)
        self.seed.proposal = proposal
        pending = driver.record_settlement_transfer()
        body = self.client.get(detail_url, headers=auth).json()
        assert body["settlement"]["amount_vnd"] == pending.amount_vnd
        assert body["settlement"]["settled_at"] is None

        settled = driver.record_settlement_ack()
        body = self.client.get(detail_url, headers=auth).json()
        assert settled.settled_at is not None
        assert body["settlement"]["settled_at"] is not None

        proposal.refresh_from_db()
        proposal.status = Proposal.Status.CLOSED
        proposal.save(update_fields=["status"])
        with self.assertRaises(ValidationError):
            rate_completed_proposal(self.resident, proposal, True)
        closed = self.client.post(
            reverse("api:proposal-rating", args=[proposal.pk]),
            data={"satisfied": True},
            content_type="application/json",
            headers=auth,
        )
        assert closed.status_code == 400

        proposal.status = Proposal.Status.COMPLETED
        proposal.save(update_fields=["status"])

        rated = self.client.post(
            reverse("api:proposal-rating", args=[proposal.pk]),
            data={"satisfied": True},
            content_type="application/json",
            headers=auth,
        )
        assert rated.status_code == 201, rated.content
        assert self.client.get(detail_url, headers=auth).json()["can_rate"] is False
