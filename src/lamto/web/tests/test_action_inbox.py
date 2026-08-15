from django.urls import reverse
from django.test import override_settings

from lamto.web.action_inbox import ActionItem, action_items_for
from lamto.web.tests.test_staff_registrations import registration, setup_building
from lamto.web.views.staff_common import prepare_action_inbox


def test_pending_registration_appears_in_building_inbox(db):
    membership, unit = setup_building("Tower A", "manager-a@example.test")
    _other_membership, other_unit = setup_building("Tower B", "manager-b@example.test")
    request = registration(unit)
    registration(other_unit, phone="0901234568", email="other@example.test")

    items = [item for item in action_items_for(membership) if item.kind == "registration"]

    assert len(items) == 1
    assert items[0].title == request.full_name
    assert items[0].url == reverse("web:staff-registration-detail", args=[request.pk])


@override_settings(LANGUAGE_CODE="en")
def test_inbox_kind_filter_uses_static_label_instead_of_item_title():
    item = ActionItem(
        kind="registration",
        title="Nguyen Van A",
        summary="A-1",
        target_type="RegistrationRequest",
        target_id=1,
        url="/s/registrations/1/",
    )

    inbox = prepare_action_inbox([item])

    assert inbox["kind_filters"] == [
        {"value": "registration", "label": "Resident registration", "active": False}
    ]
