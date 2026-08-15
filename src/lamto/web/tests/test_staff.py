from django.test import override_settings

from lamto.web.staff import building_nav_items_for, nav_items_for


@override_settings(LANGUAGE_CODE="en")
def test_registrations_appears_in_building_navigation():
    assert "Registrations" in [str(item["label"]) for item in building_nav_items_for(None)]


@override_settings(LANGUAGE_CODE="en")
def test_announcements_appears_in_building_navigation():
    assert "Announcements" in [str(item["label"]) for item in building_nav_items_for(None)]


@override_settings(LANGUAGE_CODE="en")
def test_top_nav_has_five_groups():
    labels = [str(item["label"]) for item in nav_items_for(None)]
    assert labels == ["Inbox", "Cases", "Finance", "Building", "Ops"]
