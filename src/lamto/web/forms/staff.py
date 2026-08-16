"""Staff workspace forms — mutations go through domain services only."""

from django import forms
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import ManagementMembership
from lamto.documents.models import Document, DocumentVersion
from lamto.finance.models import MaintenanceFundEntry
from lamto.maintenance.models import BuildingLocation, CaseCategory, ManagementQueue
from lamto.maintenance.triage import confirm_triage
from lamto.notifications.models import NotificationPreference
from lamto.notifications.services import PREFERENCE_EVENT_CHOICES
from lamto.web.forms.fields import WholeVndField


class MembershipSwitchForm(forms.Form):
    membership = forms.ModelChoiceField(
        queryset=ManagementMembership.objects.none(),
        label=_("Active membership"),
    )

    def __init__(self, *args, memberships=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["membership"].queryset = memberships or ManagementMembership.objects.none()


class ConfirmTriageForm(forms.Form):
    category = forms.ChoiceField(
        choices=CaseCategory.choices,
        label=_("Category"),
        widget=forms.Select(attrs={"class": "input"}),
    )
    urgency = forms.ChoiceField(
        # Must match lamto.maintenance.ai.URGENCIES / confirm_triage.
        choices=[
            ("LOW", _("Low")),
            ("MEDIUM", _("Medium")),
            ("HIGH", _("High")),
        ],
        label=_("Urgency"),
        widget=forms.Select(attrs={"class": "input"}),
    )
    location = forms.ModelChoiceField(
        queryset=BuildingLocation.objects.none(),
        label=_("Location"),
        widget=forms.Select(attrs={"class": "input"}),
    )
    management_queue = forms.ChoiceField(
        choices=ManagementQueue.choices,
        label=_("Management queue"),
        widget=forms.Select(attrs={"class": "input"}),
    )
    deadline_minutes = forms.TypedChoiceField(
        choices=[
            (60, _("1 hour")),
            (240, _("4 hours")),
            (480, _("8 hours")),
            (1440, _("1 day")),
            (2880, _("2 days")),
            (4320, _("3 days")),
            (10080, _("1 week")),
        ],
        coerce=int,
        widget=forms.Select(attrs={"class": "input"}),
        label=_("Deadline"),
    )

    def __init__(self, *args, building_id=None, extra_deadline_minutes=None, **kwargs):
        super().__init__(*args, **kwargs)
        if building_id is not None:
            locations_qs = BuildingLocation.objects.filter(
                building_id=building_id, active=True
            ).order_by("name", "pk")
            self.fields["location"].queryset = locations_qs
            locations = list(locations_qs)
            areas = [loc for loc in locations if loc.parent_id is None]
            area_map = {area.pk: area for area in areas}
            places_by_parent = {}

            for loc in locations:
                if loc.parent_id is not None and loc.parent_id in area_map:
                    places_by_parent.setdefault(loc.parent_id, []).append(loc)

            choices = []
            if self.fields["location"].empty_label is not None:
                choices.append(("", self.fields["location"].empty_label))

            selectable_pks = []
            for area in areas:
                children = places_by_parent.get(area.pk)
                if children:
                    group_options = [
                        (area.pk, _("%(name)s (whole area)") % {"name": area.name})
                    ]
                    selectable_pks.append(area.pk)
                    for child in children:
                        group_options.append((child.pk, child.name))
                        selectable_pks.append(child.pk)
                    choices.append((area.name, group_options))
                else:
                    choices.append((area.pk, area.name))
                    selectable_pks.append(area.pk)

            self.fields["location"].choices = choices
            # One real choice for a required field is not a decision to ask for.
            if not self.is_bound and not self.initial.get("location") and len(selectable_pks) == 1:
                self.initial["location"] = selectable_pks[0]
        if extra_deadline_minutes is not None:
            choices = list(self.fields["deadline_minutes"].choices)
            if not any(int(v) == extra_deadline_minutes for v, _label in choices):
                self.fields["deadline_minutes"].choices = [
                    (
                        extra_deadline_minutes,
                        _("%(minutes)s minutes") % {"minutes": extra_deadline_minutes},
                    ),
                    *choices,
                ]

    def save(self, report, operator):
        return confirm_triage(
            report,
            operator,
            self.cleaned_data["category"],
            self.cleaned_data["urgency"],
            self.cleaned_data["location"],
            self.cleaned_data["management_queue"],
            self.cleaned_data["deadline_minutes"],
        )


class InfoRequestForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label=_("What information is missing?"))


class DeclineReportForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label=_("Reason shown to the resident"))
    confirm = forms.BooleanField(
        required=True,
        label=_("I understand this decline will be sent to the resident and cannot be undone."),
    )


class ProposalDecisionForm(forms.Form):
    """Explicit proceed/decline decision; declining is terminal and needs a reason."""

    PROCEED = "proceed"
    DECLINE = "decline"

    decision = forms.ChoiceField(
        choices=[
            (PROCEED, _("Proceed — open the work on this proposal")),
            (DECLINE, _("Do not proceed — close this proposal permanently")),
        ],
        widget=forms.RadioSelect,
        label=_("Decision"),
        error_messages={"required": _("Choose whether to proceed before recording the decision.")},
    )
    note = forms.CharField(
        required=False,
        label=_("Decision note"),
        widget=forms.Textarea(attrs={"class": "input", "rows": 3}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("decision") == self.DECLINE and not (cleaned.get("note") or "").strip():
            self.add_error(
                "note",
                _("Explain why the building is not proceeding. The note is recorded with the decision."),
            )
        return cleaned

    @property
    def proceed(self) -> bool:
        return self.cleaned_data["decision"] == self.PROCEED


class ProgressUpdateForm(forms.Form):
    """A work update is its narrative: what caused the problem and what fixed it."""

    cause = forms.CharField(label=_("Cause"), widget=forms.Textarea(attrs={"class": "input", "rows": 3}))
    result = forms.CharField(label=_("Result"), widget=forms.Textarea(attrs={"class": "input", "rows": 3}))


class RecordSettlementForm(forms.Form):
    """The whole of settling: one transfer proof (ADR 0002).

    The amount is not asked for — it is the frozen published proposal amount.
    """

    event_id = forms.CharField(max_length=66, label=_("Event ID"), widget=forms.HiddenInput())
    proof = forms.ChoiceField(choices=(), required=False, label=_("Existing transfer proof"), widget=forms.Select(attrs={"class": "input"}))
    proof_upload = forms.FileField(required=False, label=_("Upload new transfer proof"), widget=forms.ClearableFileInput(attrs={"class": "input"}))

    def __init__(self, *args, proof_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["proof"].choices = [("", _("Select transfer proof…")), *proof_choices]

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("proof") and not cleaned.get("proof_upload"):
            self.add_error("proof", _("Select existing transfer proof or upload a new one."))
        return cleaned


class NotificationPreferenceForm(forms.Form):
    """Email/push opt-in flags per material event; in-app remains required."""

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        from lamto.notifications.services import RESIDENT_PUSH_EVENT_CODES

        existing = list(NotificationPreference.objects.filter(user=user))
        email_prefs = {p.event_code: p.email_enabled for p in existing}
        push_prefs = {p.event_code: p.push_enabled for p in existing}
        for code, label in PREFERENCE_EVENT_CHOICES:
            self.fields[f"email_{code}"] = forms.BooleanField(
                label=_("Email: %(event)s") % {"event": label},
                required=False,
                initial=email_prefs.get(code, True),
            )
            if code not in RESIDENT_PUSH_EVENT_CODES:
                continue
            self.fields[f"push_{code}"] = forms.BooleanField(
                label=_("Push: %(event)s") % {"event": label},
                required=False,
                initial=push_prefs.get(code, True),
            )

    def save(self):
        if self.user is None:
            raise ValidationError(_("User is required."))
        from lamto.notifications.services import RESIDENT_PUSH_EVENT_CODES

        for code, _label in PREFERENCE_EVENT_CHOICES:
            defaults = {"email_enabled": bool(self.cleaned_data.get(f"email_{code}"))}
            if code in RESIDENT_PUSH_EVENT_CODES and f"push_{code}" in self.fields:
                defaults["push_enabled"] = bool(self.cleaned_data.get(f"push_{code}"))
            NotificationPreference.objects.update_or_create(
                user=self.user,
                event_code=code,
                defaults=defaults,
            )


class CreateProposalForm(forms.Form):
    """Management-entered proposal draft; the quotation uploads on prepare."""

    amount_vnd = WholeVndField(label=_("Amount (VND)"))
    contractor_name = forms.CharField(max_length=255, label=_("Contractor name"), widget=forms.TextInput(attrs={"class": "input"}))
    purpose = forms.CharField(required=False, label=_("Purpose"), widget=forms.Textarea(attrs={"class": "input"}))
    proposed_action = forms.CharField(required=False, label=_("Proposed action"), widget=forms.Textarea(attrs={"class": "input"}))
    expected_start = forms.DateField(
        required=False,
        label=_("Expected start"),
        widget=forms.DateInput(attrs={"type": "date", "class": "input"}),
    )
    expected_end = forms.DateField(
        required=False,
        label=_("Expected end"),
        widget=forms.DateInput(attrs={"type": "date", "class": "input"}),
    )
    quotation = forms.FileField(label=_("Quotation"), widget=forms.ClearableFileInput(attrs={"class": "input"}))
    confirm = forms.BooleanField(
        required=True,
        label=_("I understand publication freezes this proposal and it cannot be edited."),
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("expected_start")
        end = cleaned_data.get("expected_end")
        if bool(start) != bool(end):
            self.add_error("expected_start", _("Provide both start and end dates, or neither."))
            self.add_error("expected_end", _("Provide both start and end dates, or neither."))
        elif start and end and end < start:
            self.add_error("expected_end", _("End date cannot be before start date."))
        return cleaned_data


class PublishLedgerEntryForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label=_("I confirm this settled expense is ready for the resident ledger."),
    )


class StandaloneProposalForm(CreateProposalForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("purpose", "proposed_action", "expected_start", "expected_end"):
            self.fields[name].required = True


class RecordFundSourceForm(forms.Form):
    """Fund source draft; the evidence uploads on prepare."""

    entry_type = forms.ChoiceField(
        choices=[
            (MaintenanceFundEntry.EntryType.OPENING_BALANCE, _("Opening balance")),
            (MaintenanceFundEntry.EntryType.INFLOW, _("Inflow")),
        ],
        label=_("Entry type"),
        widget=forms.Select(attrs={"class": "input"}),
    )
    amount_vnd = WholeVndField(label=_("Amount (VND)"))
    evidence = forms.FileField(
        label=_("Evidence"), widget=forms.ClearableFileInput(attrs={"class": "input"})
    )
