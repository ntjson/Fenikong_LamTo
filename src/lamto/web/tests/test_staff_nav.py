
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.template.loader import render_to_string
from django.urls import reverse

from lamto.accounts.models import Building, ManagementMembership
from lamto.web.staff import finance_nav_items_for, gate_nav_items_for, nav_items_for


@override_settings(LANGUAGE_CODE="en", ROOT_URLCONF="lamto.config.urls")
class ManagementShellTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Nav Building")
        self.user = get_user_model().objects.create_user(
            email="manager@example.test", password="secret", display_name="Manager"
        )
        self.membership = ManagementMembership.objects.create(
            user=self.user, building=self.building
        )

    def _login(self, user):
        self.client.force_login(user)

    def test_management_user_sees_staff_areas(self):
        labels = [str(item["label"]) for item in nav_items_for(self.membership)]
        for label in (
            "Inbox",
            "Cases",
            "Finance",
            "Building",
            "Ops",
        ):
            self.assertIn(label, labels)
        self.assertEqual(len(labels), 5)
        self.assertEqual(
            [str(item["label"]) for item in finance_nav_items_for(self.membership)],
            ["Proposals", "New proposal", "Settlements", "Fund"],
        )
        self.assertEqual(
            [str(item["label"]) for item in gate_nav_items_for(self.membership)],
            ["Review", "Registrations", "Readers", "Activity"],
        )

    def test_base_template_uses_the_product_identity(self):
        html = render_to_string("web/base.html")

        self.assertIn('rel="icon"', html)
        self.assertIn('lamto-mark.png', html)
        self.assertIn('alt=""', html)
        # One brand on both sides of sign-in: "Làm Tổ Management" / "Làm Tổ Quản lý".
        self.assertIn('Làm Tổ', html)
        self.assertNotIn('LÀM TỔ', html)

    def test_public_shell_template_carries_brand_and_stylesheet_without_authenticated_chrome(self):
        html = render_to_string("web/public/shell.html")

        self.assertIn('rel="icon"', html)
        self.assertIn('web/app.css', html)
        self.assertIn('lamto-mark.png', html)
        self.assertIn('Làm Tổ', html)
        self.assertIn('<main id="main" class="site-main"', html)
        self.assertIn('class="public"', html)

        # No authenticated chrome
        self.assertNotIn('logout', html)
        self.assertNotIn('membership-switcher', html)
        self.assertNotIn('staff-nav', html)
        self.assertNotIn('Sign out', html)
        self.assertNotIn('Đăng xuất', html)

    def test_non_management_user_is_denied_staff_home(self):
        resident = get_user_model().objects.create_user(
            email="resident@example.test", password="secret", display_name="Resident"
        )
        self._login(resident)
        self.assertEqual(self.client.get(reverse("web:staff-home")).status_code, 403)

    def test_switch_building_returns_to_inbox(self):
        other = Building.objects.create(name="Other Building")
        selected = ManagementMembership.objects.create(user=self.user, building=other)
        self._login(self.user)
        response = self.client.post(
            reverse("web:switch-building"), {"building": selected.pk}
        )
        self.assertRedirects(response, reverse("web:action-inbox"))
        self.assertEqual(self.client.session["active_management_id"], selected.pk)
