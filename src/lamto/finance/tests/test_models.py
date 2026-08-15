from django.test import SimpleTestCase

from lamto.accounts.models import ManagementMembership
from lamto.finance.models import (
    MaintenanceFundEntry,
    FundEntryVerification,
    Settlement,
    Proposal,
    ProposalVersion,
)


class FinanceMembershipModelTests(SimpleTestCase):
    def test_finance_attribution_uses_management_memberships(self):
        for model, field in (
            (Proposal, "creator_membership"),
            (ProposalVersion, "creator_membership"),
            (Settlement, "transfer_recorded_by"),
            (Settlement, "ack_recorded_by"),
            (MaintenanceFundEntry, "recorder"),
            (FundEntryVerification, "membership"),
        ):
            self.assertIs(
                model._meta.get_field(field).related_model,
                ManagementMembership,
            )
