"""problem+json exception handler unit tests (spec 3.1)."""

from django.http import Http404
from django.test import SimpleTestCase
from rest_framework import exceptions

from lamto.api.problems import (
    PROBLEM_CONTENT_TYPE,
    OccupancySelectionRequired,
    problem_exception_handler,
)


class ProblemHandlerTests(SimpleTestCase):
    def _handle(self, exc):
        return problem_exception_handler(exc, {"view": None, "request": None})

    def test_validation_error_carries_per_field_codes(self):
        response = self._handle(
            exceptions.ValidationError({"month": ["month requires a year."]})
        )
        assert response.status_code == 400
        assert response.content_type == PROBLEM_CONTENT_TYPE
        assert response.data["code"] == "validation_failed"
        assert response.data["status"] == 400
        assert response.data["type"] == "about:blank"
        assert response.data["title"]
        field_error = response.data["errors"]["month"][0]
        assert field_error["message"] == "month requires a year."
        assert field_error["code"] == "invalid"

    def test_http404_maps_to_not_found(self):
        response = self._handle(Http404("hidden"))
        assert response.status_code == 404
        assert response.data["code"] == "not_found"
        # Existence is not revealed and no internal identifiers leak.
        assert "hidden" not in str(response.data)

    def test_not_authenticated_code(self):
        response = self._handle(exceptions.NotAuthenticated())
        assert response.status_code == 401
        assert response.data["code"] == "not_authenticated"

    def test_permission_denied_code(self):
        response = self._handle(exceptions.PermissionDenied())
        assert response.status_code == 403
        assert response.data["code"] == "permission_denied"

    def test_throttled_code(self):
        response = self._handle(exceptions.Throttled())
        assert response.status_code == 429
        assert response.data["code"] == "throttled"

    def test_occupancy_selection_required_is_422(self):
        response = self._handle(OccupancySelectionRequired())
        assert response.status_code == 422
        assert response.data["code"] == "occupancy_selection_required"

    def test_unhandled_exception_returns_none(self):
        assert self._handle(RuntimeError("boom")) is None
