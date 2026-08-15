"""OpenAPI drift gate (spec 3.1, 5.4): regenerate and fail on any diff."""

import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase

SCHEMA_PATH = (
    Path(settings.BASE_DIR).parent.parent / "docs" / "api" / "openapi-v1.yaml"
)
CLIENT_MODELS = (
    Path(settings.BASE_DIR).parent.parent
    / "app"
    / "packages"
    / "lamto_api"
    / "lib"
    / "src"
    / "model"
)
REGENERATE = "python manage.py spectacular --file docs/api/openapi-v1.yaml"


class OpenApiDriftTests(SimpleTestCase):
    def test_committed_schema_matches_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            generated_path = Path(tmp) / "openapi-v1.yaml"
            call_command(
                "spectacular",
                "--file",
                str(generated_path),
                "--validate",
                "--fail-on-warn",
            )
            generated = generated_path.read_text()
        assert SCHEMA_PATH.exists(), f"schema file missing; run: {REGENERATE}"
        assert generated == SCHEMA_PATH.read_text(), (
            f"docs/api/openapi-v1.yaml is stale; regenerate with: {REGENERATE}"
        )

    def test_schema_covers_every_api_route(self):
        content = SCHEMA_PATH.read_text()
        for route in (
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/auth/logout-all",
            "/api/v1/me",
            "/api/v1/me/notification-preferences",
            "/api/v1/ledger",
            "/api/v1/fund/summary",
            "/api/v1/fund/series",
            "/api/v1/reports",
            "/api/v1/proposals",
            "/api/v1/locations",
            "/api/v1/notifications",
            "/api/v1/devices",
        ):
            assert route in content, f"{route} missing from committed schema"
        # spectacular names the <int:pk> parameter {id} when it can infer a
        # model, {pk} otherwise; either spelling proves the route is present.
        assert (
            "/api/v1/ledger/{id}" in content or "/api/v1/ledger/{pk}" in content
        ), "ledger detail route missing from committed schema"
        assert (
            "/api/v1/reports/{id}" in content or "/api/v1/reports/{pk}" in content
        ), "report detail route missing from committed schema"
        assert (
            "/api/v1/reports/{id}/photos" in content
            or "/api/v1/reports/{pk}/photos" in content
        ), "report photos upload route missing from committed schema"
        assert (
            "/api/v1/cases/{id}/rating" in content
            or "/api/v1/cases/{pk}/rating" in content
        ), "case rating route missing from committed schema"
        assert (
            "/api/v1/proposals/{id}" in content
            or "/api/v1/proposals/{pk}" in content
        ), "proposal detail route missing from committed schema"
        assert (
            "/api/v1/proposals/{id}/rating" in content
            or "/api/v1/proposals/{pk}/rating" in content
        ), "proposal rating route missing from committed schema"
        assert (
            "/api/v1/notifications/{id}/read" in content
            or "/api/v1/notifications/{pk}/read" in content
        ), "notification mark-read route missing from committed schema"
        assert "/api/v1/devices/{install_id}" in content, (
            "device delete route missing from committed schema"
        )
        assert "/api/v1/documents/" in content, (
            "document download route missing from committed schema"
        )

    def test_fund_series_range_response_is_plain_string(self):
        import yaml

        schema = yaml.safe_load(SCHEMA_PATH.read_text())
        range_schema = schema["components"]["schemas"]["FundSeries"]["properties"][
            "range"
        ]
        assert range_schema == {"type": "string"}


    def test_schema_includes_rfc9457_problem_component(self):
        content = SCHEMA_PATH.read_text()
        # Component schema name from ProblemSerializer (clarification 3).
        assert "\n    Problem:" in content, "Problem component missing from schema"
        for field in ("type:", "title:", "status:", "code:"):
            assert field in content
        assert "application/problem+json" in content

    def test_registration_email_generates_as_optional_string(self):
        import yaml

        schema = yaml.safe_load(SCHEMA_PATH.read_text())
        email = schema["components"]["schemas"]["RegistrationCreateRequest"][
            "properties"
        ]["email"]
        assert email == {"type": "string"}

    def test_generated_registration_models_do_not_print_secrets(self):
        request = (CLIENT_MODELS / "registration_create_request.g.dart").read_text()
        submission = (CLIENT_MODELS / "registration_submission.g.dart").read_text()
        request_start = request.index("String toString()")
        submission_start = submission.index("String toString()")
        request_to_string = request[
            request_start : request.index("\n  }\n}", request_start)
        ]
        submission_to_string = submission[
            submission_start : submission.index("\n  }\n}", submission_start)
        ]

        assert "password" not in request_to_string
        assert "statusToken" not in submission_to_string

    def test_tenant_routes_document_occupancy_header(self):
        """Optional X-LamTo-Occupancy is a header parameter on each tenant path."""
        import yaml

        schema = yaml.safe_load(SCHEMA_PATH.read_text())
        paths = schema["paths"]
        detail_key = (
            "/api/v1/ledger/{id}"
            if "/api/v1/ledger/{id}" in paths
            else "/api/v1/ledger/{pk}"
        )
        tenant_ops = (
            paths["/api/v1/ledger"]["get"],
            paths[detail_key]["get"],
            paths["/api/v1/fund/summary"]["get"],
            paths["/api/v1/reports"]["post"],
            paths["/api/v1/proposals"]["get"],
            paths[
                "/api/v1/proposals/{id}"
                if "/api/v1/proposals/{id}" in paths
                else "/api/v1/proposals/{pk}"
            ]["get"],
            paths[
                "/api/v1/proposals/{id}/rating"
                if "/api/v1/proposals/{id}/rating" in paths
                else "/api/v1/proposals/{pk}/rating"
            ]["post"],
            paths["/api/v1/locations"]["get"],
            paths["/api/v1/notifications"]["get"],
        )
        for operation in tenant_ops:
            names = {
                (param.get("name") if isinstance(param, dict) else None)
                for param in operation.get("parameters", [])
            }
            assert "X-LamTo-Occupancy" in names, (
                f"X-LamTo-Occupancy header missing from {operation.get('operationId')}"
            )
        # Non-tenant routes must not require the occupancy header.
        login_params = paths["/api/v1/auth/login"]["post"].get("parameters") or []
        login_names = {
            (p.get("name") if isinstance(p, dict) else None) for p in login_params
        }
        assert "X-LamTo-Occupancy" not in login_names
