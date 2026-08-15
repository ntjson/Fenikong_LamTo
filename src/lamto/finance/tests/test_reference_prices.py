"""Tests for synthetic reference price set and price comparison in the finance domain."""

from __future__ import annotations

import pytest

from lamto.finance.reference_prices import (
    ComparisonPosition,
    ReferencePrice,
    compare_price,
    get_reference_price,
    load_reference_prices,
)
from lamto.maintenance.models import CaseCategory


def test_reference_price_fixture_schema():
    """Every fixture entry must have average, minimum, maximum, sample_count, and min <= avg <= max."""
    prices = load_reference_prices()
    assert len(prices) > 0

    for category_code, entry in prices.items():
        assert isinstance(entry, ReferencePrice)
        assert entry.category == category_code
        assert isinstance(entry.average, int)
        assert isinstance(entry.minimum, int)
        assert isinstance(entry.maximum, int)
        assert isinstance(entry.sample_count, int)
        assert entry.minimum > 0
        assert entry.average > 0
        assert entry.maximum > 0
        assert entry.sample_count > 0
        assert entry.minimum <= entry.average <= entry.maximum


def test_elevator_reference_price_lookup():
    """Elevator category has synthetic reference price with seeded figures."""
    elevator_ref = get_reference_price(CaseCategory.ELEVATOR)
    assert elevator_ref is not None
    assert elevator_ref.category == CaseCategory.ELEVATOR
    assert elevator_ref.average == 450_000_000
    assert elevator_ref.minimum == 380_000_000
    assert elevator_ref.maximum == 520_000_000
    assert elevator_ref.sample_count == 12


def test_missing_categories_have_no_reference_price():
    """All 10 non-elevator categories have no reference price."""
    missing_categories = [
        CaseCategory.WATER_LEAK,
        CaseCategory.ELECTRICAL_FAULT,
        CaseCategory.HEATING_COOLING,
        CaseCategory.LIGHTING,
        CaseCategory.DOOR_LOCK,
        CaseCategory.APPLIANCE,
        CaseCategory.STRUCTURAL,
        CaseCategory.CLEANLINESS,
        CaseCategory.NOISE,
        CaseCategory.OTHER,
    ]
    assert len(missing_categories) == 10

    for category in missing_categories:
        assert get_reference_price(category) is None


@pytest.mark.parametrize(
    "amount_vnd,expected_position,expected_pct,expected_direction",
    [
        # Inside range, above average (460M vs 450M -> +10M / 450M = 2.22% -> 2% above)
        (460_000_000, ComparisonPosition.WITHIN_RANGE, 2, "above"),
        # Inside range, below average (440M vs 450M -> -10M / 450M = 2.22% -> 2% below)
        (440_000_000, ComparisonPosition.WITHIN_RANGE, 2, "below"),
        # Inside range, exactly equal to average (450M -> 0% above)
        (450_000_000, ComparisonPosition.WITHIN_RANGE, 0, "above"),
        # Inside range, at minimum boundary
        (380_000_000, ComparisonPosition.WITHIN_RANGE, 16, "below"),
        # Inside range, at maximum boundary
        (520_000_000, ComparisonPosition.WITHIN_RANGE, 16, "above"),
        # Above range (715M vs 450M -> +265M / 450M = 58.88% -> 59% above)
        (715_000_000, ComparisonPosition.ABOVE_RANGE, 59, "above"),
        # Below range (340M vs 450M -> -110M / 450M = 24.44% -> 24% below)
        (340_000_000, ComparisonPosition.BELOW_RANGE, 24, "below"),
        # Below range with demo default quote (18.5M vs 450M -> -431.5M / 450M = 95.88% -> 96% below)
        (18_500_000, ComparisonPosition.BELOW_RANGE, 96, "below"),
    ],
)
def test_compare_price_positions_and_percentage_rounding(
    amount_vnd, expected_position, expected_pct, expected_direction
):
    comparison = compare_price(CaseCategory.ELEVATOR, amount_vnd)
    assert comparison is not None
    assert comparison.position == expected_position
    assert comparison.percentage == expected_pct
    assert comparison.direction == expected_direction
    assert comparison.reference_price is not None



@pytest.mark.parametrize("invalid_amount", [0, -1, -500_000])
def test_compare_price_rejects_invalid_amount(invalid_amount):
    with pytest.raises(ValueError):
        compare_price(CaseCategory.ELEVATOR, invalid_amount)


def test_compare_price_for_missing_category_returns_none_comparison():
    comparison = compare_price(CaseCategory.WATER_LEAK, 10_000_000)
    assert comparison is None
