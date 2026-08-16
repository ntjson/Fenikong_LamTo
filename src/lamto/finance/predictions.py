"""Prediction recording and formatting services for finance."""

from __future__ import annotations

from typing import Any

from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import gettext as _

from lamto.accounts.models import ManagementMembership
from lamto.finance.ai import get_price_band_for_case
from lamto.finance.models import PricePrediction
from lamto.finance.reference_prices import (
    PriceBand,
    ReferencePrice,
    compare_price_against_band,
    get_reference_price,
)
from lamto.maintenance.models import MaintenanceCase


def format_price_comparison(
    band: PriceBand | ReferencePrice,
    amount_vnd: int,
    reasoning: str = "",
) -> dict[str, Any]:
    """Format price comparison ticker line and directional arrow."""
    comparison = compare_price_against_band(band, amount_vnd)
    min_val = getattr(band, "minimum_vnd", getattr(band, "minimum", 0))
    max_val = getattr(band, "maximum_vnd", getattr(band, "maximum", 0))
    range_text = f"{intcomma(min_val)} – {intcomma(max_val)} VND"

    if comparison.direction == "equal":
        arrow = ""
        arrow_class = ""
        comparison_text = str(_("Equal to the reference price"))
    elif comparison.direction == "above":
        arrow = "↑"
        arrow_class = "price-comparison-arrow-above"
        comparison_text = str(
            _("%(pct)s%% above the reference price (around %(range)s)")
            % {"pct": comparison.percentage, "range": range_text}
        )
    else:
        arrow = "↓"
        arrow_class = "price-comparison-arrow-below"
        comparison_text = str(
            _("%(pct)s%% below the reference price (around %(range)s)")
            % {"pct": comparison.percentage, "range": range_text}
        )

    return {
        "direction": comparison.direction,
        "percentage": comparison.percentage,
        "position": comparison.position.value,
        "arrow": arrow,
        "arrow_class": arrow_class,
        "comparison_text": comparison_text,
        "range_text": range_text,
        "reasoning": reasoning,
    }


def evaluate_and_record_price_comparison(
    case: MaintenanceCase,
    membership: ManagementMembership,
    amount_vnd: int,
) -> dict[str, Any]:
    """Evaluate predicted/fallback price comparison against amount and record a PricePrediction row."""
    if amount_vnd <= 0:
        raise ValueError(_("Amount must be a positive integer."))

    ref = get_reference_price(case.category)
    if ref is None:
        cat_label = case.get_category_display()
        msg = str(
            _("Price predictions not yet supported for %(category)s. Currently available for Elevator only.")
            % {"category": cat_label}
        )
        return {
            "supported": False,
            "error": msg,
            "formatted": {
                "message": msg,
            },
        }

    band, reasoning, source = get_price_band_for_case(case)
    if band is None:
        cat_label = case.get_category_display()
        msg = str(
            _("Price predictions not yet supported for %(category)s. Currently available for Elevator only.")
            % {"category": cat_label}
        )
        return {
            "supported": False,
            "error": msg,
            "formatted": {
                "message": msg,
            },
        }

    formatted = format_price_comparison(band, amount_vnd, reasoning=reasoning)

    prediction = PricePrediction.objects.create(
        building=case.building,
        case=case,
        category=case.category,
        amount_vnd=amount_vnd,
        minimum_vnd=band.minimum_vnd,
        central_vnd=band.central_vnd,
        maximum_vnd=band.maximum_vnd,
        reasoning=reasoning,
        source=source,
        requested_by=membership,
    )

    return {
        "id": prediction.pk,
        "category": case.category,
        "amount_vnd": amount_vnd,
        "band": {
            "minimum_vnd": band.minimum_vnd,
            "central_vnd": band.central_vnd,
            "maximum_vnd": band.maximum_vnd,
        },
        "reasoning": reasoning,
        "source": source,
        "is_fallback": source == PricePrediction.Source.FALLBACK,
        "direction": formatted["direction"],
        "percentage": formatted["percentage"],
        "position": formatted["position"],
        "formatted": formatted,
    }
