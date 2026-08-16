"""Tests for the price comparison endpoint in the Management workspace."""

from __future__ import annotations

import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from lamto.audit.models import AuditEvent
from lamto.finance.models import PricePrediction, Proposal
from lamto.finance.reference_prices import PriceBand
from lamto.maintenance.models import CaseCategory
from lamto.testing.factories import PILOT_PASSWORD, PilotDomainDriver, seed_pilot_world


class ProposalPriceCompareEndpointTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="Price Compare Web Test",
            create_sample_report=False,
        )
        self.driver = PilotDomainDriver(self.seed)
        self.elevator_report = self.driver.submit_report(
            "Elevator motor broken",
            "Price Compare Web Test / Thang máy A",
        )
        self.elevator_case = self.driver.confirm_triage_case()

        self.water_report = self.driver.submit_report(
            "Water leakage in hall",
            "Price Compare Web Test / Sảnh",
        )
        from lamto.maintenance.triage import confirm_triage
        self.water_case = confirm_triage(
            self.water_report,
            operator=self.seed.management_users[0],
            category=CaseCategory.WATER_LEAK,
            urgency="MEDIUM",
            location=self.water_report.selected_location,
            management_queue="PLUMBING",
            deadline_minutes=120,
        )
        self.manager = self.seed.management_users[0]

    def _login_manager(self):
        self.client.login(username=self.manager.email, password=PILOT_PASSWORD)

    def test_endpoint_requires_management_session(self):
        url = reverse("web:proposal-price-compare", kwargs={"pk": self.elevator_case.pk})
        response = self.client.post(
            url,
            data=json.dumps({"amount_vnd": 460_000_000}),
            content_type="application/json",
        )
        # Unauthenticated redirects to login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_endpoint_refuses_case_from_another_building(self):
        other_seed = seed_pilot_world(
            building_name="Other Building",
            create_sample_report=False,
        )
        other_driver = PilotDomainDriver(other_seed)
        other_driver.submit_report("Other lift issue", "Other Building / Lift")
        other_case = other_driver.confirm_triage_case()

        self._login_manager()
        url = reverse("web:proposal-price-compare", kwargs={"pk": other_case.pk})
        response = self.client.post(
            url,
            data=json.dumps({"amount_vnd": 460_000_000}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_endpoint_rejects_non_post(self):
        self._login_manager()
        url = reverse("web:proposal-price-compare", kwargs={"pk": self.elevator_case.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_endpoint_rejects_invalid_json(self):
        self._login_manager()
        url = reverse("web:proposal-price-compare", kwargs={"pk": self.elevator_case.pk})
        response = self.client.post(
            url,
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_endpoint_rejects_non_positive_amount(self):
        self._login_manager()
        url = reverse("web:proposal-price-compare", kwargs={"pk": self.elevator_case.pk})
        for bad_amount in [0, -100, "abc"]:
            with self.subTest(bad_amount=bad_amount):
                response = self.client.post(
                    url,
                    data=json.dumps({"amount_vnd": bad_amount}),
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)

    def test_uncovered_category_returns_coverage_limit_without_provider_call(self):
        self._login_manager()
        url = reverse("web:proposal-price-compare", kwargs={"pk": self.water_case.pk})
        with patch("lamto.finance.ai.urlopen") as mock_urlopen:
            response = self.client.post(
                url,
                data=json.dumps({"amount_vnd": 50_000_000}),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            mock_urlopen.assert_not_called()
            data = response.json()
            self.assertFalse(data.get("supported", True))
            self.assertIn("Chưa hỗ trợ dự đoán giá cho", data["formatted"]["message"])
            self.assertIn("Hiện chỉ có Thang máy.", data["formatted"]["message"])

    def test_elevator_case_calls_prediction_and_returns_id_and_formatted_strings(self):
        self._login_manager()
        url = reverse("web:proposal-price-compare", kwargs={"pk": self.elevator_case.pk})

        fake_band = PriceBand(
            category=CaseCategory.ELEVATOR,
            minimum_vnd=390_000_000,
            central_vnd=460_000_000,
            maximum_vnd=530_000_000,
        )

        initial_audit_count = AuditEvent.objects.count()
        with patch("lamto.finance.predictions.get_price_band_for_case") as mock_get_band:
            mock_get_band.return_value = (
                fake_band,
                "Dự toán phù hợp với phạm vi đại tu linh kiện.",
                PricePrediction.Source.PREDICTED,
            )

            response = self.client.post(
                url,
                data=json.dumps({"amount_vnd": 460_000_000}),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Asserts prediction id is returned
            self.assertIn("id", data)
            self.assertIsInstance(data["id"], int)

            # Asserts formatted strings
            self.assertEqual(data["amount_vnd"], 460_000_000)
            self.assertEqual(data["direction"], "equal")
            self.assertEqual(data["percentage"], 0)
            self.assertEqual(data["formatted"]["comparison_text"], "Bằng giá tham chiếu")
            self.assertEqual(data["formatted"]["range_text"], "390.000.000 – 530.000.000 VND")
            self.assertEqual(data["formatted"]["reasoning"], "Dự toán phù hợp với phạm vi đại tu linh kiện.")

            # Exactly one prediction record written
            self.assertEqual(PricePrediction.objects.count(), 1)
            prediction = PricePrediction.objects.first()
            self.assertEqual(prediction.pk, data["id"])
            self.assertEqual(prediction.amount_vnd, 460_000_000)
            self.assertEqual(prediction.source, PricePrediction.Source.PREDICTED)

            # Assert nothing written to audit log or proposals
            self.assertEqual(AuditEvent.objects.count(), initial_audit_count)
            self.assertEqual(Proposal.objects.count(), 0)

    def test_fallback_call_returns_fallback_reasoning_and_reference_band(self):
        self._login_manager()
        url = reverse("web:proposal-price-compare", kwargs={"pk": self.elevator_case.pk})

        with patch("lamto.finance.ai.urlopen", side_effect=Exception("network down")):
            response = self.client.post(
                url,
                data=json.dumps({"amount_vnd": 440_000_000}),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()

            self.assertEqual(data["source"], PricePrediction.Source.FALLBACK)
            self.assertTrue(data["is_fallback"])
            self.assertEqual(data["band"]["minimum_vnd"], 380_000_000)
            self.assertEqual(data["band"]["central_vnd"], 450_000_000)
            self.assertEqual(data["band"]["maximum_vnd"], 520_000_000)
            self.assertEqual(data["formatted"]["reasoning"], "Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.")
            self.assertIn("Thấp hơn giá tham chiếu 2%", data["formatted"]["comparison_text"])
            self.assertEqual(data["formatted"]["arrow"], "↓")
            self.assertEqual(data["formatted"]["arrow_class"], "price-comparison-arrow-below")
