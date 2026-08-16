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
class PriceBand:
    category: str
    minimum_vnd: int
    central_vnd: int
    maximum_vnd: int

    @property
    def minimum(self) -> int:
        return self.minimum_vnd

    @property
    def average(self) -> int:
        return self.central_vnd

    @property
    def central(self) -> int:
        return self.central_vnd

    @property
    def maximum(self) -> int:
        return self.maximum_vnd


@dataclass(frozen=True)
class ReferencePrice:
    category: str
    average: int
    minimum: int
    maximum: int
    sample_count: int

    @property
    def minimum_vnd(self) -> int:
        return self.minimum

    @property
    def central_vnd(self) -> int:
        return self.average

    @property
    def central(self) -> int:
        return self.average

    @property
    def maximum_vnd(self) -> int:
        return self.maximum

    def to_band(self) -> PriceBand:
        return PriceBand(
            category=self.category,
            minimum_vnd=self.minimum,
            central_vnd=self.average,
            maximum_vnd=self.maximum,
        )


@dataclass(frozen=True)
class PriceComparison:
    position: ComparisonPosition
    percentage: int
    direction: str  # "above" | "below" | "equal"
    reference_price: ReferencePrice | PriceBand


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


def compare_price_against_band(
    band: PriceBand | ReferencePrice, amount_vnd: int
) -> PriceComparison:
    """Compare a proposed quotation amount against a supplied price band."""
    if amount_vnd <= 0:
        raise ValueError(_("Amount must be a positive integer."))

    central = getattr(band, "central_vnd", getattr(band, "average", None))
    minimum = getattr(band, "minimum_vnd", getattr(band, "minimum", None))
    maximum = getattr(band, "maximum_vnd", getattr(band, "maximum", None))

    diff = amount_vnd - central
    pct = round(abs(diff) / central * 100)
    if diff > 0:
        direction = "above"
    elif diff < 0:
        direction = "below"
    else:
        direction = "equal"

    if minimum <= amount_vnd <= maximum:
        position = ComparisonPosition.WITHIN_RANGE
    elif amount_vnd > maximum:
        position = ComparisonPosition.ABOVE_RANGE
    else:
        position = ComparisonPosition.BELOW_RANGE

    return PriceComparison(
        position=position,
        percentage=pct,
        direction=direction,
        reference_price=band,
    )


def compare_price(
    category_or_band: str | CaseCategory | PriceBand | ReferencePrice, amount_vnd: int
) -> PriceComparison | None:
    """Compare a proposed quotation amount against a category's reference price or a supplied band."""
    if isinstance(category_or_band, (PriceBand, ReferencePrice)):
        return compare_price_against_band(category_or_band, amount_vnd)

    ref = get_reference_price(category_or_band)
    if ref is None:
        return None
    return compare_price_against_band(ref, amount_vnd)


