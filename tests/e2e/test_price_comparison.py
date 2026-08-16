"""End-to-end Playwright tests for quotation price comparison against synthetic reference prices."""

from __future__ import annotations

import tempfile
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright, expect

from lamto.maintenance.models import CaseCategory
from lamto.maintenance.triage import confirm_triage
from lamto.testing.factories import PILOT_PASSWORD, PilotDomainDriver, seed_pilot_world


class PriceComparisonE2ETests(StaticLiveServerTestCase):
    def _fixture_teardown(self):
        # Bypass global table truncation (which fails on security-restricted trigger tables)
        pass

    def setUp(self):
        super().setUp()
        self.seed = seed_pilot_world(
            building_name="E2E Price Comparison Building",
            create_sample_report=False,
        )
        self.driver = PilotDomainDriver(self.seed)

    def test_price_comparison_client_side_e2e(self):
        """End-to-end browser test verifying Compare button interactions, copy, and file persistence."""
        # Create elevator report and confirm triage to case
        self.driver.submit_report(
            "Elevator makes loud noise",
            "Goldmark City / Tầng 1 / Thang máy A",
        )
        elevator_case = self.driver.confirm_triage_case()

        # Create water leak report and case (uncovered category)
        water_report = self.driver.submit_report(
            "Water leaking from ceiling",
            "Goldmark City / Tầng 1 / Sảnh chính",
        )
        water_case = confirm_triage(
            water_report,
            operator=self.seed.management_users[0],
            category=CaseCategory.WATER_LEAK,
            urgency="MEDIUM",
            location=water_report.selected_location,
            management_queue="PLUMBING",
            deadline_minutes=120,
        )

        manager = self.seed.management_users[0]

        # Create temporary PDF quotation
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 sample quotation")
            pdf_path = f.name

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Log in as management account
                page.goto(f"{self.live_server_url}/accounts/login/")
                page.fill('input[name="username"]', manager.email)
                page.fill('input[name="password"]', PILOT_PASSWORD)
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle")

                # Navigate to elevator proposal create page
                page.goto(f"{self.live_server_url}/s/cases/{elevator_case.pk}/propose/")
                page.wait_for_load_state("networkidle")

                # Set file input
                page.set_input_files('input[name="quotation"]', pdf_path)
                file_val = page.eval_on_selector('input[name="quotation"]', "el => el.files.length")
                self.assertEqual(file_val, 1)

                # Check that persistent hint is removed
                hint_text = page.locator("span.hint", has_text="Giá tham chiếu là dữ liệu mẫu mô phỏng").or_(
                    page.locator("span.hint", has_text="Reference prices are synthetic sample data")
                )
                expect(hint_text).to_have_count(0)

                compare_button = page.locator("button[data-price-compare]")
                result_locator = page.locator("[data-price-comparison-result]")

                is_vietnamese = "So sánh" in compare_button.inner_text()

                # 1. Compare with empty amount -> asks for amount
                page.fill('input[name="amount_vnd"]', "")
                compare_button.click()
                if is_vietnamese:
                    expect(result_locator).to_contain_text("Nhập số tiền để so sánh.")
                else:
                    expect(result_locator).to_contain_text("Enter an amount to compare.")
                # Assert file input remains populated
                self.assertEqual(page.eval_on_selector('input[name="quotation"]', "el => el.files.length"), 1)

                # 2. Inside range (460,000,000 -> 2% above reference price)
                page.fill('input[name="amount_vnd"]', "460000000")
                compare_button.click()
                if is_vietnamese:
                    expect(result_locator).to_contain_text("Cao hơn giá tham chiếu 2% (khoảng 380.000.000 – 520.000.000 VND)")
                else:
                    expect(result_locator).to_contain_text("2% above the reference price (around 380,000,000 – 520,000,000 VND)")
                expect(page.locator(".price-comparison-arrow.price-comparison-arrow-above")).to_contain_text("↑")
                self.assertEqual(page.eval_on_selector('input[name="quotation"]', "el => el.files.length"), 1)

                # 3. Above range (715,000,000 -> 59% above reference price)
                page.fill('input[name="amount_vnd"]', "715000000")
                compare_button.click()
                if is_vietnamese:
                    expect(result_locator).to_contain_text("Cao hơn giá tham chiếu 59% (khoảng 380.000.000 – 520.000.000 VND)")
                else:
                    expect(result_locator).to_contain_text("59% above the reference price (around 380,000,000 – 520,000,000 VND)")
                expect(page.locator(".price-comparison-arrow.price-comparison-arrow-above")).to_contain_text("↑")
                self.assertEqual(page.eval_on_selector('input[name="quotation"]', "el => el.files.length"), 1)

                # 4. Below range (340,000,000 -> 24% below reference price)
                page.fill('input[name="amount_vnd"]', "340000000")
                compare_button.click()
                if is_vietnamese:
                    expect(result_locator).to_contain_text("Thấp hơn giá tham chiếu 24% (khoảng 380.000.000 – 520.000.000 VND)")
                else:
                    expect(result_locator).to_contain_text("24% below the reference price (around 380,000,000 – 520,000,000 VND)")
                expect(page.locator(".price-comparison-arrow.price-comparison-arrow-below")).to_contain_text("↓")
                self.assertEqual(page.eval_on_selector('input[name="quotation"]', "el => el.files.length"), 1)

                # 4a. Exact equality (450,000,000 -> equal to reference price, no arrow)
                page.fill('input[name="amount_vnd"]', "450000000")
                compare_button.click()
                if is_vietnamese:
                    expect(result_locator).to_contain_text("Bằng giá tham chiếu")
                else:
                    expect(result_locator).to_contain_text("Equal to the reference price")
                expect(page.locator(".price-comparison-arrow")).to_have_count(0)
                self.assertEqual(page.eval_on_selector('input[name="quotation"]', "el => el.files.length"), 1)

                # 4b. Thousands separators: the number input keeps the first dot,
                # so "460.000.000" reaches the handler as "460.000000". It must be
                # refused, not read as 460.
                page.fill('input[name="amount_vnd"]', "")
                page.type('input[name="amount_vnd"]', "460.000.000")
                compare_button.click()
                if is_vietnamese:
                    expect(result_locator).to_contain_text("không dùng dấu phân cách")
                else:
                    expect(result_locator).to_contain_text(
                        "Enter the amount in whole VND, with no separators."
                    )
                # The browser sees a whole 460 and would happily submit it, so the
                # form field is the one that has to refuse it (see WholeVndField).
                self.assertEqual(
                    page.eval_on_selector('input[name="amount_vnd"]', "el => el.value"),
                    "460.000000",
                )
                self.assertEqual(page.eval_on_selector('input[name="quotation"]', "el => el.files.length"), 1)

                # 5. Non-elevator category (Water leak)
                page.goto(f"{self.live_server_url}/s/cases/{water_case.pk}/propose/")
                page.wait_for_load_state("networkidle")
                page.set_input_files('input[name="quotation"]', pdf_path)
                page.fill('input[name="amount_vnd"]', "50000000")

                water_compare = page.locator("button[data-price-compare]")
                water_result = page.locator("[data-price-comparison-result]")
                water_compare.click()
                if is_vietnamese:
                    expect(water_result).to_contain_text("Chưa hỗ trợ dự đoán giá cho")
                    expect(water_result).to_contain_text("Hiện chỉ có Thang máy.")
                else:
                    expect(water_result).to_contain_text("Price predictions not yet supported for Water leak. Currently available for Elevator only.")
                self.assertEqual(page.eval_on_selector('input[name="quotation"]', "el => el.files.length"), 1)

                # 6. Standalone proposal page offers NO Compare button
                page.goto(f"{self.live_server_url}/s/proposals/new/")
                page.wait_for_load_state("networkidle")
                expect(page.locator("button[data-price-compare]")).to_have_count(0)

                browser.close()
        finally:
            Path(pdf_path).unlink(missing_ok=True)
