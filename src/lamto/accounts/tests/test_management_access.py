from django.core.exceptions import PermissionDenied
from django.test import TestCase

from lamto.accounts.models import Building, ManagementMembership, User
from lamto.accounts.services import require_management


class RequireManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = Building.objects.create(name="B1")
        cls.other = Building.objects.create(name="B2")
        cls.manager = User.objects.create_user(email="m@x.vn", password="pw", display_name="M")
        cls.outsider = User.objects.create_user(email="o@x.vn", password="pw", display_name="O")
        cls.membership = ManagementMembership.objects.create(
            user=cls.manager, building=cls.building
        )

    def test_active_member_passes(self):
        got = require_management(self.manager, self.building.pk)
        self.assertEqual(got.pk, self.membership.pk)

    def test_non_member_denied(self):
        with self.assertRaises(PermissionDenied):
            require_management(self.outsider, self.building.pk)

    def test_wrong_building_denied(self):
        with self.assertRaises(PermissionDenied):
            require_management(self.manager, self.other.pk)

    def test_inactive_membership_denied(self):
        ManagementMembership.objects.filter(pk=self.membership.pk).update(active=False)
        with self.assertRaises(PermissionDenied):
            require_management(self.manager, self.building.pk)

    def test_membership_unique_per_user_building(self):
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            ManagementMembership.objects.create(user=self.manager, building=self.building)
