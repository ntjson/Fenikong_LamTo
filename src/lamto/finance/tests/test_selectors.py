from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from lamto.accounts.models import Building
from lamto.finance.models import MaintenanceFund, MaintenanceFundEntry
from lamto.finance.selectors import (
    FUND_SERIES_RANGE_KEYS,
    fund_period_flows,
    fund_series,
    fund_series_from_entries,
    verified_fund_entries,
)


class FundSelectorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="Selector Building")
        cls.fund = MaintenanceFund.objects.create(building=cls.building)

    def _entry(self, entry_type, amount, recorded_at, key):
        return MaintenanceFundEntry.objects.create(
            fund=self.fund,
            entry_type=entry_type,
            amount_vnd=amount,
            source_key=key,
            recorded_at=recorded_at,
        )

    def test_period_flows_windows_and_signs(self):
        now = timezone.now()
        self._entry("OPENING_BALANCE", 1_000_000, now - timedelta(days=5), "k-open")
        self._entry("INFLOW", 200_000, now - timedelta(days=40), "k-old-inflow")
        inflows, outflows = fund_period_flows(self.building.pk, days=30)
        # Unverified entries are excluded entirely by the verified bar.
        verified_pks = set(
            verified_fund_entries(self.building.pk).values_list("pk", flat=True)
        )
        assert all(
            pk in verified_pks
            for pk in MaintenanceFundEntry.objects.filter(
                verification__isnull=False
            ).values_list("pk", flat=True)
        )
        assert isinstance(inflows, int) and isinstance(outflows, int)

    def test_other_building_excluded(self):
        other = Building.objects.create(name="Other Building")
        MaintenanceFund.objects.create(building=other)
        assert verified_fund_entries(other.pk).count() == 0

    def test_fund_entry_rejects_future_recorded_at(self):
        with self.assertRaises(ValidationError):
            self._entry(
                "INFLOW", 1, timezone.now() + timedelta(days=1), "k-future"
            )

    def test_fund_entry_accepts_current_recorded_at(self):
        entry = self._entry("INFLOW", 1, timezone.now(), "k-current")
        assert entry.pk is not None


class FundSeriesTests(TestCase):
    """Pure bucketing core: no DB rows needed, entries passed as tuples."""

    TODAY = date(2026, 7, 20)

    @staticmethod
    def _hcm(y, m, d, hour=12):
        # Naive-local helper: build an aware UTC datetime that lands on the
        # given Asia/Ho_Chi_Minh (UTC+7) calendar day at `hour` local.
        return datetime(y, m, d, hour - 7, tzinfo=dt_timezone.utc)

    def test_invalid_range_key_raises(self):
        with self.assertRaises(ValueError):
            fund_series_from_entries([], range_key="7d", today=self.TODAY)

    def test_30d_daily_buckets_and_window(self):
        series = fund_series_from_entries([], range_key="30d", today=self.TODAY)
        assert len(series) == 30
        assert series[0]["period_start"] == date(2026, 6, 21)
        assert series[-1]["period_start"] == date(2026, 7, 20)

    def test_monthly_buckets_span_calendar_months(self):
        six = fund_series_from_entries([], range_key="6m", today=self.TODAY)
        twelve = fund_series_from_entries([], range_key="12m", today=self.TODAY)
        assert [row["period_start"] for row in six] == [
            date(2026, 2, 1), date(2026, 3, 1), date(2026, 4, 1),
            date(2026, 5, 1), date(2026, 6, 1), date(2026, 7, 1),
        ]
        assert twelve[0]["period_start"] == date(2025, 8, 1)
        assert twelve[-1]["period_start"] == date(2026, 7, 1)

    def test_seed_running_balance_and_empty_bucket_fill(self):
        entries = [
            (self._hcm(2025, 12, 10), "OPENING_BALANCE", 80_000_000),  # pre-window
            (self._hcm(2026, 3, 5), "INFLOW", 20_000_000),
            (self._hcm(2026, 6, 9), "OUTFLOW", -15_000_000),
        ]
        series = fund_series_from_entries(entries, range_key="6m", today=self.TODAY)
        by_start = {row["period_start"]: row for row in series}
        assert by_start[date(2026, 2, 1)] == {
            "period_start": date(2026, 2, 1),
            "inflows_vnd": 0, "outflows_vnd": 0, "balance_vnd": 80_000_000,
        }
        assert by_start[date(2026, 3, 1)]["inflows_vnd"] == 20_000_000
        assert by_start[date(2026, 3, 1)]["balance_vnd"] == 100_000_000
        # Empty April/May carry the balance forward.
        assert by_start[date(2026, 4, 1)]["balance_vnd"] == 100_000_000
        assert by_start[date(2026, 5, 1)]["balance_vnd"] == 100_000_000
        assert by_start[date(2026, 6, 1)]["outflows_vnd"] == -15_000_000
        assert series[-1]["balance_vnd"] == 85_000_000

    def test_timezone_boundary_buckets_by_hcm_day(self):
        # 2026-06-30 18:00 UTC = 2026-07-01 01:00 in Asia/Ho_Chi_Minh → July.
        entries = [(datetime(2026, 6, 30, 18, 0, tzinfo=dt_timezone.utc), "INFLOW", 1_000)]
        series = fund_series_from_entries(entries, range_key="6m", today=self.TODAY)
        by_start = {row["period_start"]: row for row in series}
        assert by_start[date(2026, 7, 1)]["inflows_vnd"] == 1_000
        assert by_start[date(2026, 6, 1)]["inflows_vnd"] == 0

    def test_reversal_stays_in_its_own_bucket(self):
        entries = [
            (self._hcm(2026, 3, 5), "INFLOW", 5_000_000),
            (self._hcm(2026, 7, 2), "REVERSAL", -5_000_000),
        ]
        series = fund_series_from_entries(entries, range_key="6m", today=self.TODAY)
        by_start = {row["period_start"]: row for row in series}
        # March keeps its historical values; only July shows the reversal.
        assert by_start[date(2026, 3, 1)]["inflows_vnd"] == 5_000_000
        assert by_start[date(2026, 3, 1)]["outflows_vnd"] == 0
        assert by_start[date(2026, 7, 1)]["outflows_vnd"] == -5_000_000
        assert series[-1]["balance_vnd"] == 0

    def test_signed_adjustments_are_classified_by_amount(self):
        entries = [
            (self._hcm(2026, 7, 1), "REVERSAL", 5_000_000),
            (self._hcm(2026, 7, 2), "REPLACEMENT", 2_000_000),
            (self._hcm(2026, 7, 3), "REVERSAL", -1_000_000),
            (self._hcm(2026, 7, 4), "REPLACEMENT", -3_000_000),
        ]
        july = fund_series_from_entries(
            entries, range_key="6m", today=self.TODAY
        )[-1]
        assert july["inflows_vnd"] == 7_000_000
        assert july["outflows_vnd"] == -4_000_000
        assert july["balance_vnd"] == 3_000_000


class FundSeriesIntegrationTests(TestCase):
    def test_verified_bar_and_last_point_match_fund_balance(self):
        from lamto.finance.fund import fund_balance
        from lamto.testing.factories import seed_pilot_world

        seed = seed_pilot_world(
            building_name="Series Building", email_prefix="fser",
            create_sample_report=False,
        )
        # An unverified direct row must not appear anywhere in the series.
        fund = MaintenanceFund.objects.get(building=seed.building)
        MaintenanceFundEntry.objects.create(
            fund=fund, entry_type="INFLOW", amount_vnd=999_999_999,
            source_key="series-unverified", recorded_at=timezone.now(),
        )
        for range_key in FUND_SERIES_RANGE_KEYS:
            series = fund_series(seed.building.pk, range_key=range_key)
            assert series[-1]["balance_vnd"] == fund_balance(
                seed.building.pk, verified_only=True
            )
            assert all(row["inflows_vnd"] < 999_999_999 for row in series)
