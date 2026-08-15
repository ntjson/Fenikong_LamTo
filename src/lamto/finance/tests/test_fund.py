from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from lamto.documents.models import Document
from lamto.evidence.models import BlockchainOutboxEvent
from lamto.finance.fund import fund_balance, get_or_create_fund, record_fund_source, verify_fund_source
from lamto.finance.models import MaintenanceFundEntry
from lamto.testing.factories import seed_pilot_world


@override_settings(LANGUAGE_CODE="en-us")  # asserts English source strings
class OffchainFundTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(building_name=f"Fund {self._testMethodName}", create_sample_report=False)
        self.recorder = self.seed.management_memberships[0]
        self.evidence = self.seed.document(Document.Kind.CONTRACT, self.recorder.user, "fund")
        self.fund = get_or_create_fund(self.seed.building)

    def test_record_and_self_confirm_are_offchain_and_move_the_balance(self):
        before = BlockchainOutboxEvent.objects.count()
        balance_before = fund_balance(self.seed.building.pk)
        entry = record_fund_source(self.fund, MaintenanceFundEntry.EntryType.INFLOW, 50_000_000, self.evidence, self.recorder)
        # The balance only counts confirmed sources, so recording alone moves nothing.
        self.assertEqual(fund_balance(self.seed.building.pk), balance_before)

        verification = verify_fund_source(entry, self.recorder)

        self.assertEqual(verification.membership, self.recorder)
        self.assertEqual(BlockchainOutboxEvent.objects.count(), before)
        self.assertEqual(fund_balance(self.seed.building.pk), balance_before + 50_000_000)

    def test_a_source_cannot_be_confirmed_twice(self):
        entry = record_fund_source(
            self.fund, MaintenanceFundEntry.EntryType.INFLOW, 1_000_000,
            self.evidence, self.recorder,
        )
        verify_fund_source(entry, self.recorder)
        with self.assertRaisesRegex(ValidationError, "already been verified"):
            verify_fund_source(entry, self.recorder)
