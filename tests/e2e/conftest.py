"""Playwright / domain PilotDriver fixtures for Task 18 e2e.

When Chromium/Playwright cannot run, tests use PilotDomainDriver which exercises
the same domain entry points as the browser suite would.

Set LAMTO_E2E_BROWSER=1 to attempt a live Chromium session (otherwise domain-only).
"""

from __future__ import annotations

import os
import tempfile

import pytest


def _browser_requested() -> bool:
    return os.getenv("LAMTO_E2E_BROWSER", "").lower() in {"1", "true", "yes"}


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def browser_available():
    if not _browser_requested():
        return False
    return _chromium_available()


@pytest.fixture
def page(browser_available):
    """Browser page when Chromium works; otherwise None (domain driver path)."""
    if not browser_available:
        yield None
        return
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    pg = context.new_page()
    try:
        yield pg
    finally:
        context.close()
        browser.close()
        playwright.stop()


@pytest.fixture
def temp_storage(settings):
    location = tempfile.mkdtemp(prefix="lamto-e2e-")
    settings.STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": location},
        },
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": location},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    return location


@pytest.fixture
def seeded_pilot(db, temp_storage):
    from lamto.testing.factories import PilotDomainDriver, seed_pilot_world

    seed = seed_pilot_world(
        building_name="E2E Pilot Building",
        create_sample_report=False,
    )
    return PilotDomainDriver(seed)
