import hashlib
import secrets
import tempfile
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from lamto.accounts.models import Building, ManagementMembership, User
from lamto.documents.access import DocumentIntegrityError
from lamto.documents.models import Document, DocumentVersion
from lamto.finance.models import Proposal
from lamto.finance.proposals import (
    create_standalone_proposal,
    publish_proposal_version,
)
from lamto.finance.settlements import record_settlement


@override_settings(
    STORAGES={
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tempfile.gettempdir() + "/lamto-explorer-tests"},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class ExplorerDocumentDownloadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="B1")
        cls.manager = User.objects.create_user(email="m@x.vn", password="pw")
        cls.membership = ManagementMembership.objects.create(
            user=cls.manager, building=cls.building
        )

    def stored_version(self, kind, tag, payload):
        storage = storages["private"]
        key = f"{tag}-{secrets.token_hex(8)}"
        storage.save(key, ContentFile(payload))
        return DocumentVersion.objects.create(
            document=Document.objects.create(building=self.building, kind=kind),
            version=1,
            storage_key=key,
            provider_version_id=key,
            filename=f"{tag}.pdf",
            content_type="application/pdf",
            byte_size=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
            uploader=self.manager,
        )

    def published_proposal(self, quotation_payload=b"%PDF-1.7 quotation"):
        quotation = self.stored_version(
            Document.Kind.QUOTATION, "quote", quotation_payload
        )
        proposal = create_standalone_proposal(self.building, self.membership)
        publish_proposal_version(
            proposal,
            self.membership,
            amount_vnd=100,
            contractor_name="Acme",
            purpose="Repair",
            proposed_action="Fix the lift",
            expected_schedule="Now",
            quotation_versions=[quotation],
            event_id="0x" + secrets.token_hex(32),
        )
        proposal.refresh_from_db()
        return proposal

    def settled_proposal(self, payload=b"%PDF-1.7 transfer-proof"):
        proposal = self.published_proposal()
        proof = self.stored_version(Document.Kind.PAYMENT_PROOF, "transfer", payload)
        Proposal.objects.filter(pk=proposal.pk).update(
            status=Proposal.Status.COMPLETED, completed_at=timezone.now()
        )
        proposal.refresh_from_db()
        record_settlement(
            proposal,
            self.membership,
            transfer=proof,
            event_id="0x" + secrets.token_hex(32),
        )
        return proposal, proof

    def document_url(self, token, sha256):
        return reverse(
            "explorer:document-download",
            kwargs={"public_token": token, "sha256": sha256},
        )

    def test_unauthenticated_get_returns_the_document_bytes(self):
        proposal, proof = self.settled_proposal()

        response = self.client.get(
            self.document_url(proposal.public_token, proof.sha256)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.7 transfer-proof")
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("inline", response["Content-Disposition"])
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_quotation_document_is_served_by_its_hash(self):
        proposal = self.published_proposal()
        quotation = proposal.current_version.quotations.get()

        response = self.client.get(
            self.document_url(proposal.public_token, quotation.sha256)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.7 quotation")
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("inline", response["Content-Disposition"])
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_quotation_of_a_superseded_version_stays_available(self):
        proposal = self.published_proposal()
        first_quotation = proposal.current_version.quotations.get()
        newer = self.stored_version(
            Document.Kind.QUOTATION, "quote-v2", b"%PDF-1.7 quotation v2"
        )
        publish_proposal_version(
            proposal,
            self.membership,
            amount_vnd=200,
            contractor_name="Acme",
            purpose="Repair",
            proposed_action="Fix the lift again",
            expected_schedule="Later",
            quotation_versions=[newer],
            event_id="0x" + secrets.token_hex(32),
        )

        response = self.client.get(
            self.document_url(proposal.public_token, first_quotation.sha256)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"%PDF-1.7 quotation")

    def test_another_proposals_quotation_hash_returns_not_found(self):
        proposal = self.published_proposal(b"%PDF-1.7 quotation A")
        other = self.published_proposal(b"%PDF-1.7 quotation B")
        other_quotation = other.current_version.quotations.get()

        response = self.client.get(
            self.document_url(proposal.public_token, other_quotation.sha256)
        )

        self.assertEqual(response.status_code, 404)

    def test_tampered_quotation_bytes_are_rejected_never_served(self):
        proposal = self.published_proposal()
        quotation = proposal.current_version.quotations.get()
        with storages["private"].open(quotation.storage_key, "wb") as file_obj:
            file_obj.write(b"%PDF-1.7 tampered-quotation")

        response = self.client.get(
            self.document_url(proposal.public_token, quotation.sha256)
        )

        self.assertEqual(response.status_code, 409)
        self.assertNotEqual(response.content, b"%PDF-1.7 tampered-quotation")

    def test_unknown_token_returns_not_found(self):
        _, proof = self.settled_proposal()

        response = self.client.get(self.document_url("not-a-real-token", proof.sha256))

        self.assertEqual(response.status_code, 404)

    def test_valid_token_with_unknown_hash_returns_not_found(self):
        proposal, _ = self.settled_proposal()

        response = self.client.get(self.document_url(proposal.public_token, "f" * 64))

        self.assertEqual(response.status_code, 404)

    def test_another_proposals_transfer_hash_returns_not_found(self):
        proposal, _proof = self.settled_proposal(b"%PDF-1.7 transfer-proof A")
        _other, other_proof = self.settled_proposal(b"%PDF-1.7 transfer-proof B")

        response = self.client.get(
            self.document_url(proposal.public_token, other_proof.sha256)
        )

        self.assertEqual(response.status_code, 404)

    def test_proposal_without_settlement_has_no_documents(self):
        proposal = self.published_proposal()

        response = self.client.get(self.document_url(proposal.public_token, "a" * 64))

        self.assertEqual(response.status_code, 404)

    def test_tampered_stored_bytes_are_rejected_never_served(self):
        proposal, proof = self.settled_proposal(b"%PDF-1.7 transfer-proof")
        with storages["private"].open(proof.storage_key, "wb") as file_obj:
            file_obj.write(b"%PDF-1.7 tampered-bytes")

        response = self.client.get(
            self.document_url(proposal.public_token, proof.sha256)
        )

        self.assertEqual(response.status_code, 409)
        self.assertNotEqual(response.content, b"%PDF-1.7 tampered-bytes")

    def test_missing_storage_object_is_rejected(self):
        proposal, proof = self.settled_proposal()
        storages["private"].delete(proof.storage_key)

        response = self.client.get(
            self.document_url(proposal.public_token, proof.sha256)
        )

        self.assertEqual(response.status_code, 409)

    def test_download_verifies_through_the_shared_integrity_reader(self):
        proposal, proof = self.settled_proposal()
        url = self.document_url(proposal.public_token, proof.sha256)

        with patch(
            "lamto.explorer.views.read_version_bytes",
            side_effect=DocumentIntegrityError("Document integrity check failed."),
        ):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 409)
