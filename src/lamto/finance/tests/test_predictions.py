"""Tests for PricePrediction model and comparison recording in the finance domain."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from lamto.accounts.models import Building, ManagementMembership
from lamto.finance.models import PricePrediction
from lamto.maintenance.models import BuildingLocation, CaseCategory, MaintenanceCase, TriageDecision
from lamto.maintenance.reporting import submit_report
from lamto.testing.factories import PILOT_PASSWORD, PilotDomainDriver, seed_pilot_world


class PricePredictionModelTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="Prediction Test Building",
            create_sample_report=False,
        )
        self.driver = PilotDomainDriver(self.seed)
        report = self.driver.submit_report("Elevator shakes", "Prediction Test Building / Sảnh chính")
        self.case = self.driver.confirm_triage_case()
        self.membership = self.seed.management_memberships[0]
        self.building = self.seed.building

    def test_create_price_prediction_record(self):
        """A prediction record holds category, amount, band, reasoning, source, who and when."""
        prediction = PricePrediction.objects.create(
            building=self.building,
            case=self.case,
            category=CaseCategory.ELEVATOR,
            amount_vnd=460_000_000,
            minimum_vnd=390_000_000,
            central_vnd=460_000_000,
            maximum_vnd=530_000_000,
            reasoning="Chi phí đại tu thang máy phù hợp với khối lượng công việc.",
            source=PricePrediction.Source.PREDICTED,
            requested_by=self.membership,
        )
        self.assertIsNotNone(prediction.pk)
        self.assertEqual(prediction.source, PricePrediction.Source.PREDICTED)
        self.assertEqual(prediction.amount_vnd, 460_000_000)
        self.assertEqual(prediction.minimum_vnd, 390_000_000)
        self.assertEqual(prediction.central_vnd, 460_000_000)
        self.assertEqual(prediction.maximum_vnd, 530_000_000)
        self.assertEqual(prediction.requested_by, self.membership)
        self.assertIsNotNone(prediction.created_at)

    def test_create_fallback_prediction_record(self):
        prediction = PricePrediction.objects.create(
            building=self.building,
            case=self.case,
            category=CaseCategory.ELEVATOR,
            amount_vnd=460_000_000,
            minimum_vnd=380_000_000,
            central_vnd=450_000_000,
            maximum_vnd=520_000_000,
            reasoning="Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.",
            source=PricePrediction.Source.FALLBACK,
            requested_by=self.membership,
        )
        self.assertEqual(prediction.source, PricePrediction.Source.FALLBACK)

    def test_evaluate_and_record_price_comparison_creates_record_and_formatted_strings(self):
        from unittest.mock import patch
        from lamto.finance.predictions import evaluate_and_record_price_comparison
        from lamto.finance.reference_prices import PriceBand

        fake_band = PriceBand(
            category=CaseCategory.ELEVATOR,
            minimum_vnd=390_000_000,
            central_vnd=460_000_000,
            maximum_vnd=530_000_000,
        )

        with patch("lamto.finance.predictions.get_price_band_for_case") as mock_get_band:
            mock_get_band.return_value = (
                fake_band,
                "Chi phí hợp lý.",
                PricePrediction.Source.PREDICTED,
            )

            # Amount is 460M -> exactly equal to central_vnd
            result = evaluate_and_record_price_comparison(
                case=self.case,
                membership=self.membership,
                amount_vnd=460_000_000,
            )

            self.assertEqual(PricePrediction.objects.count(), 1)
            saved = PricePrediction.objects.first()
            self.assertEqual(saved.amount_vnd, 460_000_000)
            self.assertEqual(saved.minimum_vnd, 390_000_000)
            self.assertEqual(saved.central_vnd, 460_000_000)
            self.assertEqual(saved.maximum_vnd, 530_000_000)
            self.assertEqual(saved.reasoning, "Chi phí hợp lý.")
            self.assertEqual(saved.source, PricePrediction.Source.PREDICTED)
            self.assertEqual(saved.requested_by, self.membership)
            self.assertEqual(saved.case, self.case)
            self.assertEqual(saved.building, self.building)

            self.assertEqual(result["id"], saved.pk)
            self.assertEqual(result["amount_vnd"], 460_000_000)
            self.assertEqual(result["direction"], "equal")
            self.assertEqual(result["percentage"], 0)
            self.assertEqual(result["formatted"]["comparison_text"], "Bằng giá tham chiếu")
            self.assertEqual(result["formatted"]["arrow"], "")
            self.assertEqual(result["formatted"]["reasoning"], "Chi phí hợp lý.")

