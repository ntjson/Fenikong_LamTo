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
from lamto.documents.models import Document, DocumentVersion
from lamto.evidence.chain import ChainRecord
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.finance.models import Proposal, VerificationObservation
from lamto.finance.proposals import (
    create_standalone_proposal,
    decide_proposal,
    publish_proposal_version,
)
from lamto.finance.publication import publish_settlement_entry
from lamto.finance.settlements import record_settlement


@override_settings(
    STORAGES={
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tempfile.gettempdir() + "/lamto-explorer-page-tests"},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class EvidenceExplorerPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="Tòa nhà Sen Vàng")
        cls.manager = User.objects.create_user(
            email="manager@sen-vang.vn",
            password="pw",
            display_name="Nguyễn Văn Quản Lý",
        )
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

    def published_proposal(self, **kwargs):
        quotation = self.stored_version(
            Document.Kind.QUOTATION, "bao-gia", b"%PDF-1.7 quotation"
        )
        proposal = create_standalone_proposal(self.building, self.membership)
        publish_proposal_version(
            proposal,
            self.membership,
            amount_vnd=kwargs.get("amount_vnd", 50_000_000),
            contractor_name=kwargs.get("contractor_name", "Công ty Thang máy Việt Nam"),
            purpose=kwargs.get("purpose", "Bảo trì định kỳ hệ thống thang máy"),
            proposed_action=kwargs.get("proposed_action", "Thay thế cáp tải và kiểm định an toàn"),
            expected_schedule=kwargs.get("expected_schedule", "Tháng 8/2026"),
            quotation_versions=[quotation],
            event_id="0x" + secrets.token_hex(32),
        )
        proposal.refresh_from_db()
        return proposal

    def settled_proposal(self, **kwargs):
        proposal = self.published_proposal(**kwargs)
        proof = self.stored_version(
            Document.Kind.PAYMENT_PROOF,
            "uy-nhiem-chi",
            b"%PDF-1.7 transfer-proof",
        )
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

    def explorer_url(self, token):
        return reverse("explorer:detail", kwargs={"public_token": token})

    def test_unknown_token_returns_not_found(self):
        response = self.client.get(self.explorer_url("not-a-real-token"))
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_get_with_valid_token_returns_ok(self):
        proposal = self.published_proposal()
        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)

    def test_proposal_summary_renders_parity_fields(self):
        proposal = self.published_proposal(
            amount_vnd=50_000_000,
            contractor_name="Công ty Thang máy Việt Nam",
            purpose="Bảo trì định kỳ hệ thống thang máy",
            proposed_action="Thay thế cáp tải và kiểm định an toàn",
        )
        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Tòa nhà Sen Vàng", content)
        self.assertIn("Công ty Thang máy Việt Nam", content)
        self.assertIn("50.000.000", content)
        self.assertIn("Bảo trì định kỳ hệ thống thang máy", content)
        self.assertIn("Thay thế cáp tải và kiểm định an toàn", content)

    def test_approvers_rendered_when_decided(self):
        proposal = self.published_proposal()
        decide_proposal(proposal, self.manager, proceed=True, note="Duyệt thực hiện")
        proposal.refresh_from_db()

        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Nguyễn Văn Quản Lý", content)

    def test_timeline_lists_multiple_published_versions_in_order(self):
        proposal = self.published_proposal(
            purpose="Phiên bản đầu tiên",
            amount_vnd=30_000_000,
        )
        quote2 = self.stored_version(
            Document.Kind.QUOTATION, "quote-v2", b"%PDF-1.7 quotation v2"
        )
        # Note: to publish a new version after v1, proposal must be in DRAFT/PUBLISHED state
        publish_proposal_version(
            proposal,
            self.membership,
            amount_vnd=45_000_000,
            contractor_name="Công ty Thang máy Miền Nam",
            purpose="Phiên bản điều chỉnh kinh phí",
            proposed_action="Thay thế thêm cáp phụ",
            expected_schedule="Tháng 9/2026",
            quotation_versions=[quote2],
            event_id="0x" + secrets.token_hex(32),
        )

        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        v1_idx = content.find("Phiên bản đề xuất #1")
        v2_idx = content.find("Phiên bản đề xuất #2")
        self.assertNotEqual(v1_idx, -1)
        self.assertNotEqual(v2_idx, -1)
        self.assertLess(v1_idx, v2_idx)
        self.assertIn("Phiên bản đầu tiên", content)
        self.assertIn("Phiên bản điều chỉnh kinh phí", content)

    def test_pre_settlement_proposal_shows_settlement_as_pending(self):
        proposal = self.published_proposal()
        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Nghiệm thu và thanh toán", content)
        self.assertIn("Đang chờ neo blockchain", content)
        self.assertIn("chưa thực hiện thanh toán", content)

    def test_settled_proposal_shows_settlement_step_and_document_link(self):
        proposal, proof = self.settled_proposal()
        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Nghiệm thu và thanh toán", content)
        self.assertIn(proof.filename, content)
        expected_doc_url = reverse(
            "explorer:document-download",
            kwargs={"public_token": proposal.public_token, "sha256": proof.sha256},
        )
        self.assertIn(expected_doc_url, content)

    def test_live_chain_confirmed_renders_with_chain_timestamp_and_verified_badge(self):
        proposal = self.published_proposal()
        event = proposal.current_version.outbox_event
        fake_time = 1770000000

        def fake_find(ev):
            return ChainRecord(
                payload_hash="0x" + ev.payload_hash,
                previous_hash="0x" + "00" * 32,
                event_type=int(ev.event_type),
                signer=ev.signer_address,
                recorded_at=fake_time,
            )

        with patch("lamto.evidence.chain.EvidenceRegistryClient") as client_cls:
            client_cls.return_value.find.side_effect = fake_find
            response = self.client.get(self.explorer_url(proposal.public_token))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Đã neo trên blockchain", content)
        self.assertIn("status-verified", content)
        self.assertIn(event.payload_hash, content)

    def test_live_chain_mismatch_renders_with_mismatch_badge_and_never_verified_or_pending(self):
        proposal, _ = self.settled_proposal()

        def fake_find(ev):
            return ChainRecord(
                payload_hash="0x" + "deadbeef" * 8,
                previous_hash="0x" + "00" * 32,
                event_type=int(ev.event_type),
                signer=ev.signer_address,
                recorded_at=1770000000,
            )

        with patch("lamto.evidence.chain.EvidenceRegistryClient") as client_cls:
            client_cls.return_value.find.side_effect = fake_find
            response = self.client.get(self.explorer_url(proposal.public_token))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Phát hiện sai lệch dữ liệu", content)
        self.assertIn("status-mismatch", content)
        # MISMATCH must never dress as verified or pending on mismatched steps
        self.assertNotIn("status-verified", content)
        self.assertNotIn("Đang chờ neo blockchain", content)

    def test_locally_signed_evidence_renders_with_local_signed_badge_and_info_tone(self):
        proposal = self.published_proposal()
        BlockchainOutboxEvent.objects.filter(
            pk=proposal.current_version.outbox_event_id
        ).update(status=BlockchainOutboxEvent.Status.LOCAL)

        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Đã ký — chưa bật neo blockchain", content)
        self.assertIn("status-info", content)

    def test_integrity_observation_honestly_absent_when_none_exists(self):
        proposal = self.published_proposal()
        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertNotIn("Xác thực tính toàn vẹn độc lập", content)

    def test_integrity_observation_rendered_with_verifier_and_timestamp_when_present(self):
        proposal, proof = self.settled_proposal()
        entry = publish_settlement_entry(proposal.settlement)
        now = timezone.now()
        VerificationObservation.objects.create(
            published_entry=entry,
            result=VerificationObservation.Result.VERIFIED,
            details={"verifier": "Đoàn Kiểm Toán Độc Lập ABC"},
            checked_document_hashes=[proof.sha256],
            checked_chain_event_ids=[proposal.current_version.outbox_event.event_id],
            observed_at=now,
        )

        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Xác thực tính toàn vẹn độc lập", content)
        self.assertIn("Bản ghi đã xác minh", content)
        self.assertIn("status-verified", content)
        self.assertIn("Đoàn Kiểm Toán Độc Lập ABC", content)

    def test_chain_unreachable_renders_stored_state_with_honest_unavailability_note(self):
        proposal = self.published_proposal()
        event = proposal.current_version.outbox_event

        with patch("lamto.evidence.chain.EvidenceRegistryClient") as client_cls:
            client_cls.return_value.find.side_effect = Exception("RPC connection failed")
            response = self.client.get(self.explorer_url(proposal.public_token))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Không thể kết nối với blockchain. Đang hiển thị trạng thái đã lưu.", content)
        self.assertIn(event.payload_hash, content)

    def test_no_public_action_triggers_document_reverification(self):
        proposal, _ = self.settled_proposal()
        entry = publish_settlement_entry(proposal.settlement)

        with patch("lamto.finance.integrity.verify_published_entry") as mock_verify:
            response = self.client.get(self.explorer_url(proposal.public_token))

        self.assertEqual(response.status_code, 200)
        mock_verify.assert_not_called()

    def test_page_is_vietnamese_only_and_plain_language_above_technical_detail(self):
        proposal = self.published_proposal()
        response = self.client.get(self.explorer_url(proposal.public_token))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn('lang="vi"', content)
        self.assertIn("Hồ sơ minh bạch chi tiêu", content)
        self.assertIn("Chuỗi bằng chứng trách nhiệm", content)
        self.assertIn("Bằng chứng kỹ thuật", content)
        self.assertIn("details class=\"technical-proof\"", content)
