from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import RequestFactory, TestCase

from lamto.accounts.models import Building, ResidentOccupancy, Unit
from lamto.accounts.tenancy import (
    SESSION_OCCUPANCY_KEY,
    TenantContext,
    resolve_resident_occupancy,
)


class ResolveResidentOccupancyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="resident@example.test", password="x", display_name="R"
        )
        cls.building_a = Building.objects.create(name="Building A")
        cls.building_b = Building.objects.create(name="Building B")
        cls.unit_a = Unit.objects.create(building=cls.building_a, label="A-101")
        cls.unit_b = Unit.objects.create(building=cls.building_b, label="B-202")
        cls.occ_a = ResidentOccupancy.objects.create(user=cls.user, unit=cls.unit_a)

    def _request(self, user):
        request = RequestFactory().get("/")
        request.user = user
        request.session = SessionStore()
        return request

    def test_no_occupancy_denied(self):
        stranger = get_user_model().objects.create_user(
            email="none@example.test", password="x", display_name="N"
        )
        with self.assertRaises(PermissionDenied):
            resolve_resident_occupancy(self._request(stranger))

    def test_sole_occupancy_auto_selected_and_pinned(self):
        request = self._request(self.user)
        occupancy, occupancies = resolve_resident_occupancy(request)
        assert occupancy.pk == self.occ_a.pk
        assert [o.pk for o in occupancies] == [self.occ_a.pk]
        assert request.session[SESSION_OCCUPANCY_KEY] == self.occ_a.pk

    def test_multiple_defaults_to_first_and_session_switches(self):
        occ_b = ResidentOccupancy.objects.create(user=self.user, unit=self.unit_b)
        request = self._request(self.user)
        occupancy, _ = resolve_resident_occupancy(request)
        assert occupancy.pk == self.occ_a.pk
        request.session[SESSION_OCCUPANCY_KEY] = occ_b.pk
        occupancy, _ = resolve_resident_occupancy(request)
        assert occupancy.pk == occ_b.pk

    def test_stale_session_falls_back_and_repins(self):
        occ_b = ResidentOccupancy.objects.create(user=self.user, unit=self.unit_b)
        request = self._request(self.user)
        request.session[SESSION_OCCUPANCY_KEY] = occ_b.pk
        ResidentOccupancy.objects.filter(pk=occ_b.pk).update(active=False)
        occupancy, _ = resolve_resident_occupancy(request)
        assert occupancy.pk == self.occ_a.pk
        assert request.session[SESSION_OCCUPANCY_KEY] == self.occ_a.pk

    def test_explicit_foreign_id_raises_404(self):
        other = get_user_model().objects.create_user(
            email="other@example.test", password="x", display_name="O"
        )
        foreign = ResidentOccupancy.objects.create(user=other, unit=self.unit_b)
        with self.assertRaises(Http404):
            resolve_resident_occupancy(
                self._request(self.user), occupancy_id=foreign.pk
            )

    def test_tenant_context_from_occupancy(self):
        context = TenantContext.from_occupancy(self.occ_a)
        assert context.building_id == self.building_a.pk
        assert context.actor == "resident"
        assert context.occupancy_id == self.occ_a.pk
        assert context.membership_id is None
