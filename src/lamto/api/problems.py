"""RFC 9457 problem+json errors with stable machine codes (spec 3.1).

`detail` is developer English; the Flutter client owns all Vietnamese
user-facing copy keyed off `code`. Never include stack traces or internal
identifiers in responses.
"""

from http import HTTPStatus

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from drf_spectacular.utils import OpenApiResponse
from rest_framework import exceptions
from rest_framework.views import exception_handler as drf_exception_handler

from lamto.api.serializers import ProblemSerializer

PROBLEM_CONTENT_TYPE = "application/problem+json"

# OpenAPI media type for documented problem responses (clarification 3).
_PROBLEM_DESCRIPTIONS = {
    400: "Validation failed (code=validation_failed).",
    401: (
        "Authentication required or failed "
        "(code=not_authenticated or authentication_failed)."
    ),
    403: "Permission denied (code=permission_denied).",
    404: "Resource not found (code=not_found).",
    409: "A request conflicts with existing state.",
    422: (
        "Occupancy selection required "
        "(code=occupancy_selection_required); send X-LamTo-Occupancy, or gate input was unusable."
    ),
    202: "Accepted for manager review (gate face enrolment).",
    503: "A dependency is unavailable (code=gate_model_unavailable).",
    429: "Too many authentication attempts (code=throttled).",
}


def problem_responses(*status_codes: int) -> dict:
    """Map HTTP statuses to reusable RFC 9457 Problem OpenAPI responses.

    Keys use the ``application/problem+json`` media type so the committed
    schema documents the wire content type the exception handler sets.
    """
    responses = {}
    for status in status_codes:
        try:
            description = _PROBLEM_DESCRIPTIONS[status]
        except KeyError as exc:
            raise ValueError(f"no Problem description for status {status}") from exc
        responses[(status, PROBLEM_CONTENT_TYPE)] = OpenApiResponse(
            response=ProblemSerializer,
            description=description,
        )
    return responses


class OccupancySelectionRequired(exceptions.APIException):
    """Multiple active occupancies and no X-LamTo-Occupancy header (spec 3.4)."""

    status_code = 422
    default_detail = (
        "Multiple active occupancies; select one with the X-LamTo-Occupancy header."
    )
    default_code = "occupancy_selection_required"


class ClientRefConflict(exceptions.APIException):
    """POST /reports retried with the same client_ref but different content (spec 3.5)."""

    status_code = 409
    default_detail = "client_ref reused with different content."
    default_code = "client_ref_conflict"


class RegistrationConflictProblem(exceptions.APIException):
    status_code = 409
    default_detail = "Registration cannot be submitted."
    default_code = "registration_conflict"


class BillVoided(exceptions.APIException):
    status_code = 409
    default_detail = "This bill was voided and can no longer be paid."
    default_code = "bill_voided"


class GateNoFaceDetected(exceptions.APIException):
    status_code, default_code, default_detail = 422, "gate_no_face_detected", "No face was detected in the image."
class GateMultipleFaces(exceptions.APIException):
    status_code, default_code, default_detail = 422, "gate_multiple_faces", "More than one face was detected in the image."
class GateFaceTooSmall(exceptions.APIException):
    status_code, default_code, default_detail = 422, "gate_face_too_small", "The face in the image is too small."
class GateFaceTooBlurry(exceptions.APIException):
    status_code, default_code, default_detail = 422, "gate_face_too_blurry", "The face in the image is too blurry."
class GateFaceUnusable(exceptions.APIException):
    status_code, default_code, default_detail = 422, "gate_face_unusable", "The image cannot be used for enrolment."
class GatePhotoRejected(exceptions.APIException):
    status_code, default_code, default_detail = 400, "gate_photo_rejected", "The upload was rejected before processing."
class GatePlateUnreadable(exceptions.APIException):
    status_code, default_code, default_detail = 422, "gate_plate_unreadable", "The plate text could not be read."
class GatePlateAlreadyRegistered(exceptions.APIException):
    status_code, default_code, default_detail = 409, "gate_plate_already_registered", "This plate is already registered in this building."
class GateModelUnavailable(exceptions.APIException):
    status_code, default_code, default_detail = 503, "gate_model_unavailable", "The face recognition model is unavailable."
class GateFaceUploadTooLarge(exceptions.APIException):
    status_code, default_code, default_detail = 413, "gate_face_upload_too_large", "The face upload exceeds the configured limit."
class GateRecognitionThrottled(exceptions.APIException):
    status_code, default_code, default_detail = 429, "gate_recognition_throttled", "This reader is sending recognition requests too quickly."
class GateDeviceUnauthenticated(exceptions.APIException):
    status_code, default_code, default_detail = 401, "gate_device_unauthenticated", "Invalid gate device credential."
class GateDeviceRevoked(GateDeviceUnauthenticated):
    default_code, default_detail = "gate_device_revoked", "This reader's credential was revoked."
class GateDeviceExpired(GateDeviceUnauthenticated):
    default_code, default_detail = "gate_device_expired", "This reader's credential has expired."


# Most specific classes first: the first isinstance() match wins.
_EXCEPTION_CODES = (
    (GateNoFaceDetected, "gate_no_face_detected"),
    (GateMultipleFaces, "gate_multiple_faces"),
    (GateFaceTooSmall, "gate_face_too_small"),
    (GateFaceTooBlurry, "gate_face_too_blurry"),
    (GateFaceUnusable, "gate_face_unusable"),
    (GatePhotoRejected, "gate_photo_rejected"),
    (GatePlateUnreadable, "gate_plate_unreadable"),
    (GatePlateAlreadyRegistered, "gate_plate_already_registered"),
    (GateModelUnavailable, "gate_model_unavailable"),
    (GateFaceUploadTooLarge, "gate_face_upload_too_large"),
    (GateRecognitionThrottled, "gate_recognition_throttled"),
    (GateDeviceRevoked, "gate_device_revoked"),
    (GateDeviceExpired, "gate_device_expired"),
    (GateDeviceUnauthenticated, "gate_device_unauthenticated"),
    (OccupancySelectionRequired, "occupancy_selection_required"),
    (RegistrationConflictProblem, "registration_conflict"),
    (ClientRefConflict, "client_ref_conflict"),
    (BillVoided, "bill_voided"),
    (exceptions.NotAuthenticated, "not_authenticated"),
    (exceptions.AuthenticationFailed, "authentication_failed"),
    (exceptions.PermissionDenied, "permission_denied"),
    (exceptions.NotFound, "not_found"),
    (exceptions.MethodNotAllowed, "method_not_allowed"),
    (exceptions.Throttled, "throttled"),
    (exceptions.ParseError, "validation_failed"),
    (exceptions.UnsupportedMediaType, "validation_failed"),
    (exceptions.ValidationError, "validation_failed"),
    (Http404, "not_found"),
    (DjangoPermissionDenied, "permission_denied"),
)


def _field_errors(detail):
    """Preserve DRF's per-field error structure while exposing machine codes."""
    if isinstance(detail, dict):
        return {key: _field_errors(value) for key, value in detail.items()}
    if isinstance(detail, list):
        return [_field_errors(item) for item in detail]
    return {"message": str(detail), "code": getattr(detail, "code", "invalid")}


def problem_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        # Not an API exception: let Django's standard 500 path handle it.
        return None
    code = next(
        (code for klass, code in _EXCEPTION_CODES if isinstance(exc, klass)), "error"
    )
    problem = {
        "type": "about:blank",
        "title": HTTPStatus(response.status_code).phrase,
        "status": response.status_code,
        "code": code,
    }
    if isinstance(exc, exceptions.ValidationError):
        problem["detail"] = "Request validation failed."
        problem["errors"] = _field_errors(exc.detail)
    elif isinstance(exc, exceptions.APIException):
        problem["detail"] = str(exc.detail)
    elif isinstance(exc, Http404):
        problem["detail"] = "Not found."
    else:  # django.core.exceptions.PermissionDenied
        problem["detail"] = "Permission denied."
    response.data = problem
    # DRF keeps an explicitly set content_type through finalize_response.
    response.content_type = PROBLEM_CONTENT_TYPE
    return response
