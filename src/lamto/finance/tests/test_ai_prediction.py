"""Tests for AI price prediction provider, contract validation, and fallback mechanisms."""

from __future__ import annotations

import json
from unittest.mock import patch
from urllib.error import URLError

from django.test import TestCase, override_settings

from lamto.finance.ai import (
    PricePredictionValidationError,
    _endpoint_url,
    get_price_band_for_case,
)
from lamto.finance.models import PricePrediction
from lamto.finance.reference_prices import PriceBand
from lamto.maintenance.models import CaseCategory
from lamto.testing.factories import PilotDomainDriver, seed_pilot_world


def valid_prediction_payload(**overrides):
    payload = {
        "minimum_vnd": 390_000_000,
        "central_vnd": 460_000_000,
        "maximum_vnd": 530_000_000,
        "reasoning": "Chi phí đại tu thang máy hợp lý với khối lượng thiết bị cần bảo trì.",
    }
    payload.update(overrides)
    return payload


def envelope(content_dict_or_str, request_id="cmpl-price-1", refusal=None):
    if refusal:
        msg = {"content": None, "refusal": refusal}
    elif isinstance(content_dict_or_str, dict):
        msg = {"content": json.dumps(content_dict_or_str)}
    else:
        msg = {"content": str(content_dict_or_str)}

    body = {"choices": [{"message": msg}]}
    if request_id is not None:
        body["id"] = request_id
    return body


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        if isinstance(self.payload, bytes):
            return self.payload
        return json.dumps(self.payload).encode()


@override_settings(
    AI_TRIAGE_URL="https://triage.example.test/v1/chat/completions",
    AI_TRIAGE_TOKEN="test-token",
    AI_TRIAGE_MODEL="gpt-4o-mini",
    AI_PRICE_MODEL="",
    AI_PRICE_TIMEOUT_SECONDS=8.0,
)
class AIPredictionTests(TestCase):
    def setUp(self):
        self.seed = seed_pilot_world(
            building_name="AI Prediction Test Building",
            create_sample_report=False,
        )
        self.driver = PilotDomainDriver(self.seed)
        self.elevator_report = self.driver.submit_report(
            "Elevator motor vibrates violently and stops between floors",
            "AI Prediction Test Building / Thang máy A",
        )
        self.elevator_case = self.driver.confirm_triage_case()

        self.water_report = self.driver.submit_report(
            "Water pipe broken in basement",
            "AI Prediction Test Building / Hầm B1",
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

    def test_endpoint_url_configuration_and_model_fallback(self):
        # When AI_PRICE_MODEL is empty, falls back to AI_TRIAGE_MODEL
        url, token, model, timeout = _endpoint_url()
        self.assertEqual(url, "https://triage.example.test/v1/chat/completions")
        self.assertEqual(token, "test-token")
        self.assertEqual(model, "gpt-4o-mini")
        self.assertEqual(timeout, 8.0)

    @override_settings(AI_PRICE_MODEL="custom-price-model", AI_PRICE_TIMEOUT_SECONDS=12.0)
    def test_custom_price_model_and_timeout(self):
        url, token, model, timeout = _endpoint_url()
        self.assertEqual(model, "custom-price-model")
        self.assertEqual(timeout, 12.0)

    @patch("lamto.finance.ai.urlopen")
    def test_successful_provider_call_returns_predicted_band_and_reasoning(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(envelope(valid_prediction_payload()))

        band, reasoning, source = get_price_band_for_case(self.elevator_case)

        self.assertIsInstance(band, PriceBand)
        self.assertEqual(band.minimum_vnd, 390_000_000)
        self.assertEqual(band.central_vnd, 460_000_000)
        self.assertEqual(band.maximum_vnd, 530_000_000)
        self.assertEqual(reasoning, "Chi phí đại tu thang máy hợp lý với khối lượng thiết bị cần bảo trì.")
        self.assertEqual(source, PricePrediction.Source.PREDICTED)

        # Verify request sent
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        sent_body = json.loads(request.data.decode())
        self.assertEqual(sent_body["model"], "gpt-4o-mini")
        self.assertEqual(sent_body["temperature"], 0)

        user_content = json.loads(sent_body["messages"][1]["content"])
        self.assertIn("category", user_content)
        self.assertIn("scope", user_content)
        self.assertIn("reference_price", user_content)
        # Provably does not contain quotation amount!
        self.assertNotIn("amount_vnd", json.dumps(user_content))
        self.assertNotIn("quotation", json.dumps(user_content))

    @patch("lamto.finance.ai.urlopen")
    def test_prompt_provably_does_not_contain_quotation_amount(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(envelope(valid_prediction_payload()))

        get_price_band_for_case(self.elevator_case)

        request = mock_urlopen.call_args.args[0]
        body_str = request.data.decode()
        # Even if manager enters 460M or 715M, that amount is never in the LLM payload
        self.assertNotIn("460000000", body_str)
        self.assertNotIn("715000000", body_str)
        self.assertNotIn("quotation_amount", body_str)

    @patch("lamto.finance.ai.urlopen", side_effect=URLError("Connection refused"))
    def test_transport_error_falls_back_to_reference_price_set(self, _mock_urlopen):
        band, reasoning, source = get_price_band_for_case(self.elevator_case)

        self.assertEqual(source, PricePrediction.Source.FALLBACK)
        self.assertEqual(band.minimum_vnd, 380_000_000)
        self.assertEqual(band.central_vnd, 450_000_000)
        self.assertEqual(band.maximum_vnd, 520_000_000)
        self.assertEqual(reasoning, "Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.")

    @patch("lamto.finance.ai.urlopen", side_effect=TimeoutError("Request timed out"))
    def test_timeout_falls_back_to_reference_price_set(self, _mock_urlopen):
        band, reasoning, source = get_price_band_for_case(self.elevator_case)

        self.assertEqual(source, PricePrediction.Source.FALLBACK)
        self.assertEqual(band.minimum_vnd, 380_000_000)
        self.assertEqual(band.central_vnd, 450_000_000)
        self.assertEqual(band.maximum_vnd, 520_000_000)
        self.assertEqual(reasoning, "Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.")

    @patch("lamto.finance.ai.urlopen")
    def test_malformed_json_falls_back(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(b"NOT JSON AT ALL")

        band, reasoning, source = get_price_band_for_case(self.elevator_case)

        self.assertEqual(source, PricePrediction.Source.FALLBACK)
        self.assertEqual(band.central_vnd, 450_000_000)
        self.assertEqual(reasoning, "Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.")

    @patch("lamto.finance.ai.urlopen")
    def test_contract_key_mismatch_falls_back(self, mock_urlopen):
        # Missing reasoning, has unexpected key
        mock_urlopen.return_value = FakeResponse(
            envelope({"minimum_vnd": 390_000_000, "central_vnd": 460_000_000, "extra": "data"})
        )

        band, reasoning, source = get_price_band_for_case(self.elevator_case)

        self.assertEqual(source, PricePrediction.Source.FALLBACK)
        self.assertEqual(band.central_vnd, 450_000_000)
        self.assertEqual(reasoning, "Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.")

    @patch("lamto.finance.ai.urlopen")
    def test_out_of_order_band_falls_back(self, mock_urlopen):
        # central < minimum
        mock_urlopen.return_value = FakeResponse(
            envelope({
                "minimum_vnd": 500_000_000,
                "central_vnd": 400_000_000,
                "maximum_vnd": 600_000_000,
                "reasoning": "Chi phí...",
            })
        )

        band, reasoning, source = get_price_band_for_case(self.elevator_case)

        self.assertEqual(source, PricePrediction.Source.FALLBACK)
        self.assertEqual(band.central_vnd, 450_000_000)
        self.assertEqual(reasoning, "Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.")

    @patch("lamto.finance.ai.urlopen")
    def test_model_refusal_falls_back(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(envelope(None, refusal="I cannot estimate this."))

        band, reasoning, source = get_price_band_for_case(self.elevator_case)

        self.assertEqual(source, PricePrediction.Source.FALLBACK)
        self.assertEqual(band.central_vnd, 450_000_000)
        self.assertEqual(reasoning, "Dự đoán AI không khả dụng — dùng giá tham chiếu mẫu.")

    @patch("lamto.finance.ai.urlopen")
    def test_uncovered_category_makes_no_provider_call(self, mock_urlopen):
        band, reasoning, source = get_price_band_for_case(self.water_case)

        self.assertIsNone(band)
        self.assertEqual(reasoning, "")
        self.assertEqual(source, "")
        mock_urlopen.assert_not_called()
