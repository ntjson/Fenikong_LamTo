"""A completed proposal points at the settlement it is waiting on.

The proposal page resolved an action panel for every status except COMPLETED,
so the one screen a Management account reaches from the case — and from the
settlement item in the action inbox — was a dead end: the timeline said
settlement was the current step, and the action column said no action was
assigned to this membership.
"""

from django.test import TestCase, override_settings
from django.urls import reverse

from lamto.finance.models import Proposal
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world


@override_settings(LANGUAGE_CODE="en", ROOT_URLCONF="lamto.config.urls")
class ProposalSettlementHandoffTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(building_name="Handoff B", email_prefix="psh")
        driver = PilotDomainDriver(self.seed)
        driver.submit_report("Lift jerks", "Lift 2")
        driver.confirm_triage_case()
        driver.publish_proposal()
        driver.decide_proposal(proceed=True)
        driver.complete_assigned_work()
        self.proposal = self.seed.proposal
        self.operator = self.seed.management_memberships[0]
        self.client.force_login(self.operator.user)
        session = self.client.session
        session["active_management_id"] = self.operator.pk
        session.save()

    def _get_detail(self):
        return self.client.get(
            reverse("web:proposal-detail", kwargs={"pk": self.proposal.pk})
        )

    def test_completed_proposal_awaiting_settlement_offers_the_settlement_step(self):
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, Proposal.Status.COMPLETED)
        self.assertFalse(hasattr(self.proposal, "settlement"))

        response = self._get_detail()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["action_panel"], "settle")
        self.assertContains(
            response,
            reverse("web:settlement-record", kwargs={"pk": self.proposal.pk}),
        )
        self.assertNotContains(response, "No action is assigned to this membership")

    def test_settled_proposal_moves_past_the_settlement_step(self):
        PilotDomainDriver(self.seed).record_settlement()

        response = self._get_detail()

        self.assertNotEqual(response.context["action_panel"], "settle")
        self.assertNotContains(
            response,
            reverse("web:settlement-record", kwargs={"pk": self.proposal.pk}),
        )
