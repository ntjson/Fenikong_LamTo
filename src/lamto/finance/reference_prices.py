"""Synthetic reference price set and price comparison logic for the finance domain."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
from typing import Any

from django.utils.translation import gettext_lazy as _

from lamto.maintenance.models import CaseCategory, normalize_category

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "reference_prices.json"


class ComparisonPosition(StrEnum):
    WITHIN_RANGE = "within_range"
    ABOVE_RANGE = "above_range"
    BELOW_RANGE = "below_range"


@dataclass(frozen=True)
class ReferencePrice:
    category: str
    average: int
    minimum: int
    maximum: int
    sample_count: int


@dataclass(frozen=True)
class PriceComparison:
    position: ComparisonPosition
    percentage: int
    direction: str  # "above" | "below" | "equal"
    reference_price: ReferencePrice


def load_reference_prices() -> dict[str, ReferencePrice]:
    """Load the synthetic reference price set from the finance fixture."""
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        raw: dict[str, dict[str, Any]] = json.load(f)

    return {
        category: ReferencePrice(
            category=category,
            average=data["average"],
            minimum=data["minimum"],
            maximum=data["maximum"],
            sample_count=data["sample_count"],
        )
        for category, data in raw.items()
    }


def get_reference_price(category: str | CaseCategory) -> ReferencePrice | None:
    """Look up a category's reference price in the synthetic reference price set."""
    code = normalize_category(str(category))
    prices = load_reference_prices()
    return prices.get(code)


def compare_price(category: str | CaseCategory, amount_vnd: int) -> PriceComparison | None:
    """Compare a proposed quotation amount against a category's reference price."""
    if amount_vnd <= 0:
        raise ValueError(_("Amount must be a positive integer."))

    ref = get_reference_price(category)
    if ref is None:
        return None

    diff = amount_vnd - ref.average
    pct = round(abs(diff) / ref.average * 100)
    direction = "above" if diff >= 0 else "below"

    if ref.minimum <= amount_vnd <= ref.maximum:
        position = ComparisonPosition.WITHIN_RANGE
    elif amount_vnd > ref.maximum:
        position = ComparisonPosition.ABOVE_RANGE
    else:
        position = ComparisonPosition.BELOW_RANGE

    return PriceComparison(
        position=position,
        percentage=pct,
        direction=direction,
        reference_price=ref,
    )

