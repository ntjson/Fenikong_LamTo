"""Resident API serializers (spec 3). Later tasks append to this module."""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from lamto.maintenance.models import IssueReport


class ProblemSerializer(serializers.Serializer):
    """RFC 9457 problem+json body with a LamTo stable machine ``code`` (spec 3.1).

    ``detail`` is developer English; the Flutter client owns Vietnamese UI copy
    keyed off ``code``. ``errors`` is present only for validation failures.
    """

    type = serializers.CharField(
        help_text="Problem type URI reference; usually about:blank.",
    )
    title = serializers.CharField(
        help_text="Short human-readable summary (HTTP status phrase).",
    )
    status = serializers.IntegerField(help_text="HTTP status code.")
    code = serializers.CharField(
        help_text=(
            "Stable machine code for client branching "
            "(e.g. validation_failed, authentication_failed, not_authenticated, "
            "permission_denied, not_found, occupancy_selection_required, throttled)."
        ),
    )
    detail = serializers.CharField(
        required=False,
        help_text="Developer-English explanation; not shown raw to residents.",
    )
    errors = serializers.DictField(
        required=False,
        help_text=(
            "Per-field validation errors when code is validation_failed. "
            "Values are lists of {message, code} objects (may nest for non-field errors)."
        ),
    )


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text="Email or Vietnamese phone number.")
    # trim_whitespace=False: passwords may legitimately contain spaces.
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    expiry = serializers.DateTimeField()


class OccupancySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit_label = serializers.CharField()
    building_name = serializers.CharField()


class NotificationPreferenceSerializer(serializers.Serializer):
    event_code = serializers.CharField()
    email_enabled = serializers.BooleanField()
    push_enabled = serializers.BooleanField()


class NotificationPreferenceUpdateItemSerializer(serializers.Serializer):
    """One preference row for PATCH /me/notification-preferences."""

    event_code = serializers.CharField(max_length=64)
    email_enabled = serializers.BooleanField(required=False)
    push_enabled = serializers.BooleanField(required=False)

    def validate(self, data):
        if "email_enabled" not in data and "push_enabled" not in data:
            raise serializers.ValidationError(
                "At least one of email_enabled or push_enabled is required."
            )
        return data


class NotificationPreferenceUpdateSerializer(serializers.Serializer):
    preferences = NotificationPreferenceUpdateItemSerializer(many=True, allow_empty=False)


class LogoutInstallIdSerializer(serializers.Serializer):
    """Optional body field for logout Device deactivation (spec 7.2)."""

    install_id = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=64,
        help_text="Deactivate this install's FCM Device on logout (also accepted via X-Install-Id).",
    )


class MeSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    email = serializers.EmailField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    occupancies = OccupancySerializer(many=True)
    notification_preferences = NotificationPreferenceSerializer(many=True)


class LedgerFilterSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False, min_value=2000, max_value=2100)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)

    def validate(self, data):
        if "month" in data and "year" not in data:
            raise serializers.ValidationError({"month": "month requires a year."})
        return data


class LedgerEntryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    contractor_name = serializers.CharField()
    actual_cost_vnd = serializers.IntegerField()
    published_at = serializers.DateTimeField()
    integrity_status = serializers.CharField(source="effective_integrity_status")
    evidence_level = serializers.SerializerMethodField()
    # Same concept, same wire name as the detail payload (§6.3(6) story).
    what_was_fixed = serializers.SerializerMethodField(
        help_text="Resident-visible narrative of work completed."
    )

    def get_evidence_level(self, entry) -> str:
        from lamto.evidence.models import evidence_level

        return evidence_level(entry.settlement.outbox_event.status)

    def get_what_was_fixed(self, entry) -> str:
        from lamto.finance.selectors import ledger_story_fields

        return ledger_story_fields(entry)["what_was_fixed"]


class VerificationSerializer(serializers.Serializer):
    decision = serializers.CharField()
    verified_by = serializers.CharField()
    verified_at = serializers.DateTimeField()


class LedgerDocumentSerializer(serializers.Serializer):
    label = serializers.CharField()
    filename = serializers.CharField()
    sha256 = serializers.CharField()
    download_url = serializers.CharField()


class ProofEventSerializer(serializers.Serializer):
    event_id = serializers.CharField()
    event_type = serializers.IntegerField()
    status = serializers.CharField()
    evidence_level = serializers.CharField()
    transaction_hash = serializers.CharField(allow_blank=True)


class ProofSerializer(serializers.Serializer):
    evidence_level = serializers.CharField()
    anchoring_backend = serializers.CharField(allow_blank=True)
    payload_hash = serializers.CharField()
    events = ProofEventSerializer(many=True)
    proposal_version = serializers.JSONField()
    settlement = serializers.JSONField()


class LedgerEntryDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    contractor_name = serializers.CharField()
    actual_cost_vnd = serializers.IntegerField()
    published_at = serializers.DateTimeField()
    proposed_amount_vnd = serializers.IntegerField(allow_null=True)
    integrity_status = serializers.CharField()
    # §6.3(6) plain-language story (A1): what / why alongside amount
    # and payment verification. Sourced from work/report relations, not invented.
    what_was_fixed = serializers.CharField(
        help_text="Resident-visible narrative of work completed."
    )
    why = serializers.CharField(
        help_text="Resident-visible rationale (cause or purpose)."
    )
    explorer_url = serializers.CharField(
        allow_null=True,
        help_text="Absolute public Evidence explorer URL when anchored, null otherwise.",
    )
    payload = serializers.JSONField()
    verification = VerificationSerializer(allow_null=True)
    # Compatibility-only fields retained for the shipped Flutter contract.
    approvers = serializers.ListField(child=serializers.JSONField())
    corrections = serializers.ListField(child=serializers.JSONField())
    documents = LedgerDocumentSerializer(many=True)
    proof = ProofSerializer()


class FundSummarySerializer(serializers.Serializer):
    balance_vnd = serializers.IntegerField()
    period_days = serializers.IntegerField()
    period_inflows_vnd = serializers.IntegerField()
    period_outflows_vnd = serializers.IntegerField()


class FundSeriesPointSerializer(serializers.Serializer):
    period_start = serializers.DateField()
    inflows_vnd = serializers.IntegerField()
    outflows_vnd = serializers.IntegerField(
        help_text="Outflow-type amounts are stored negative; this is <= 0."
    )
    balance_vnd = serializers.IntegerField()


class FundSeriesSerializer(serializers.Serializer):
    range = serializers.CharField()
    points = FundSeriesPointSerializer(many=True)


class ReportCreateSerializer(serializers.Serializer):
    client_ref = serializers.UUIDField(
        help_text="Client-generated UUID, unique per user (spec 3.5)."
    )
    text = serializers.CharField(max_length=5000)
    is_private = serializers.BooleanField(required=False, default=False)
    location_id = serializers.IntegerField(
        help_text="Active BuildingLocation id in the resolved occupancy building."
    )


class ReportSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    status = serializers.ChoiceField(choices=IssueReport.Status.choices)
    is_private = serializers.BooleanField()
    location_path_snapshot = serializers.CharField()
    created_at = serializers.DateTimeField()


class ReportPhotoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    filename = serializers.CharField()
    sha256 = serializers.CharField()
    download_url = serializers.CharField()


class ReportPhotoUploadSerializer(serializers.Serializer):
    photo = serializers.FileField(help_text="JPEG/PNG image; scanned by ClamAV before storage.")


class ReportWorkUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cause = serializers.CharField()
    result = serializers.CharField()
    created_at = serializers.DateTimeField()


class ReportCaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category = serializers.CharField()
    urgency = serializers.CharField()
    deadline_at = serializers.DateTimeField()
    active = serializers.BooleanField()
    completed_at = serializers.DateTimeField(allow_null=True)
    closed_at = serializers.DateTimeField(allow_null=True)
    updates = ReportWorkUpdateSerializer(many=True)
    can_rate = serializers.BooleanField()


class ReportDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    status = serializers.ChoiceField(choices=IssueReport.Status.choices)
    declined_reason = serializers.CharField(allow_null=True)
    is_private = serializers.BooleanField()
    open_info_request = serializers.DictField(allow_null=True)
    location_path_snapshot = serializers.CharField()
    unit_label = serializers.CharField()
    created_at = serializers.DateTimeField()
    triage_status = serializers.CharField(allow_null=True)
    category = serializers.CharField(allow_null=True)
    photos = ReportPhotoSerializer(many=True)
    cases = ReportCaseSerializer(many=True)
    ledger_entry_ids = serializers.ListField(child=serializers.IntegerField())


class InfoReplySerializer(serializers.Serializer):
    text = serializers.CharField()


class InfoReplyResultSerializer(serializers.Serializer):
    report_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=IssueReport.Status.choices)


class CaseRatingSerializer(serializers.Serializer):
    satisfied = serializers.BooleanField()
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)


class CaseRatingResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    case_id = serializers.IntegerField()
    satisfied = serializers.BooleanField()


class ProposalSupportingDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    filename = serializers.CharField()
    sha256 = serializers.CharField()
    download_url = serializers.CharField()


class ProposalVersionSerializer(serializers.Serializer):
    number = serializers.IntegerField()
    published_at = serializers.DateTimeField()
    evidence_level = serializers.CharField()
    supporting_documents = ProposalSupportingDocumentSerializer(many=True)


class ProposalProgressSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cause = serializers.CharField()
    result = serializers.CharField()
    created_at = serializers.DateTimeField()


class ProposalSettlementSerializer(serializers.Serializer):
    amount_vnd = serializers.IntegerField()
    settled_at = serializers.DateTimeField()


class ProposalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    case_id = serializers.IntegerField(allow_null=True)
    building_id = serializers.IntegerField()
    status = serializers.CharField()
    completed_at = serializers.DateTimeField(allow_null=True)
    closed_at = serializers.DateTimeField(allow_null=True)
    purpose = serializers.CharField(source="current_version.purpose")
    proposed_action = serializers.CharField(source="current_version.proposed_action")
    amount_vnd = serializers.IntegerField(source="current_version.amount_vnd")
    contractor_name = serializers.CharField(source="current_version.contractor_name")
    expected_schedule = serializers.CharField(source="current_version.expected_schedule")
    explorer_url = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    settlement = serializers.SerializerMethodField()
    can_rate = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_explorer_url(self, proposal) -> str | None:
        from lamto.explorer.urls import explorer_public_url

        request = self.context.get("request") if self.context else None
        return explorer_public_url(proposal.public_token, request=request)

    @extend_schema_field(ProposalVersionSerializer(many=True))
    def get_versions(self, proposal) -> list[dict]:
        from django.urls import reverse

        from lamto.api.downloads import issue_download_token
        from lamto.evidence.models import evidence_level

        request = self.context["request"]
        rows = []
        for version in proposal.versions.all():
            documents = []
            for quotation in version.quotations.all():
                documents.append(
                    {
                        "id": quotation.pk,
                        "filename": quotation.filename,
                        "sha256": quotation.sha256,
                        "download_url": reverse(
                            "api:document-download",
                            args=[issue_download_token(request.user.pk, quotation.pk)],
                        ),
                    }
                )
            rows.append(
                {
                    "number": version.number,
                    "published_at": version.created_at,
                    "evidence_level": evidence_level(version.outbox_event.status),
                    "supporting_documents": documents,
                }
            )
        return ProposalVersionSerializer(rows, many=True).data

    @extend_schema_field(ProposalProgressSerializer(many=True))
    def get_progress(self, proposal) -> list[dict]:
        updates = proposal.case.updates.all() if proposal.case_id else proposal.updates.all()
        return ProposalProgressSerializer(updates, many=True).data

    @extend_schema_field(ProposalSettlementSerializer(allow_null=True))
    def get_settlement(self, proposal) -> dict | None:
        from django.core.exceptions import ObjectDoesNotExist

        try:
            settlement = proposal.settlement
        except ObjectDoesNotExist:
            return None
        return ProposalSettlementSerializer(
            {
                "amount_vnd": settlement.amount_vnd,
                "settled_at": settlement.settled_at,
            }
        ).data

    def get_can_rate(self, proposal) -> bool:
        return (
            proposal.case_id is None
            and proposal.status == "COMPLETED"
            and proposal.completed_at is not None
            and not proposal.has_current_user_rating
        )


class ProposalRatingResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    proposal_id = serializers.IntegerField()
    satisfied = serializers.BooleanField()


class LocationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    parent_id = serializers.IntegerField(allow_null=True)


class NotificationFeedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    event_code = serializers.CharField()
    event_key = serializers.CharField(
        help_text=(
            "Deep-link reference '{code}:{entity}:{id}' (spec 6.3/7.4). Entity ids "
            "are resident-visible resources the API re-authorizes on fetch. "
            "Authorization-neutral and non-sensitive: codes/entity/ids only — "
            "no PII, bodies, or tokens."
        ),
    )
    subject = serializers.CharField()
    body = serializers.CharField()
    created_at = serializers.DateTimeField()
    read_at = serializers.DateTimeField(allow_null=True)


class NotificationFilterSerializer(serializers.Serializer):
    event_code = serializers.CharField(required=False, max_length=80)
    unread = serializers.BooleanField(required=False)


class DeviceRegisterSerializer(serializers.Serializer):
    install_id = serializers.CharField(
        max_length=64, help_text="Stable per-install client UUID (spec 7.2)."
    )
    fcm_token = serializers.CharField(max_length=512)
    platform = serializers.ChoiceField(choices=["IOS", "ANDROID"])
    app_version = serializers.CharField(
        max_length=32, required=False, allow_blank=True, default=""
    )


class DeviceSerializer(serializers.Serializer):
    install_id = serializers.CharField()
    platform = serializers.CharField()
    active = serializers.BooleanField()
