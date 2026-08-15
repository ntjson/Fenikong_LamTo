from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .gate_serializers import *
from .occupancy import OCCUPANCY_HEADER_PARAMETER, resolve_api_occupancy
from .problems import *
from lamto.accounts.security import client_ip
from lamto.gate.devices import authenticate_device, token_from_header, GateAuthenticationFailed, GateCredentialExpired, GateCredentialRevoked
from lamto.gate.embedding import FaceEmbedderUnavailable, FaceQualityError, FaceTooBlurry, FaceTooSmall, MultipleFacesDetected, NoFaceDetected
from lamto.gate.enrollment import PhotoRejected, PlateAlreadyRegistered, revoke_face_enrollment, revoke_plate, submit_face_enrollment, submit_plate
from lamto.gate.models import FaceEnrollment, VehiclePlate
from lamto.gate.plates import PlateFormatError
from lamto.gate.recognition import recognize_face, recognize_plate


def _plate(p):
    return {"id": p.pk, "plate": p.plate, "status": p.status, "submitted_at": p.submitted_at, "review_note": p.review_note}

def _face(f):
    return None if f is None else {"status": f.status, "submitted_at": f.submitted_at, "review_note": f.review_note}

class GateRegistrationsView(APIView):
    @extend_schema(parameters=[OCCUPANCY_HEADER_PARAMETER], responses=GateRegistrationsSerializer)
    def get(self, request):
        occupancy, _ = resolve_api_occupancy(request)
        return Response(GateRegistrationsSerializer({"face": _face(FaceEnrollment.objects.filter(occupancy=occupancy).first()), "plates": [_plate(p) for p in VehiclePlate.objects.filter(occupancy=occupancy).order_by("plate")] }).data)

class GatePlateListCreateView(APIView):
    @extend_schema(parameters=[OCCUPANCY_HEADER_PARAMETER], request=PlateCreateSerializer, responses={201: VehiclePlateSerializer})
    def post(self, request):
        occupancy, _ = resolve_api_occupancy(request)
        data = PlateCreateSerializer(data=request.data); data.is_valid(raise_exception=True)
        try: plate = submit_plate(occupancy, data.validated_data["plate"])
        except PlateFormatError: raise GatePlateUnreadable()
        except PlateAlreadyRegistered: raise GatePlateAlreadyRegistered()
        return Response(VehiclePlateSerializer(_plate(plate)).data, status=201)

class GatePlateDetailView(APIView):
    @extend_schema(parameters=[OCCUPANCY_HEADER_PARAMETER], request=None, responses={204: None})
    def delete(self, request, pk):
        occupancy, _ = resolve_api_occupancy(request)
        if not VehiclePlate.objects.filter(pk=pk, occupancy=occupancy).exists(): raise exceptions.NotFound()
        revoke_plate(occupancy, pk)
        return Response(status=204)

class GateFaceView(APIView):
    parser_classes = [parsers.MultiPartParser]
    @extend_schema(parameters=[OCCUPANCY_HEADER_PARAMETER], request=FaceUploadSerializer, responses={202: FaceEnrollmentSerializer})
    def post(self, request):
        occupancy, _ = resolve_api_occupancy(request)
        data = FaceUploadSerializer(data=request.data); data.is_valid(raise_exception=True)
        try: enrollment = submit_face_enrollment(occupancy, data.validated_data["photo"])
        except PhotoRejected as e: raise GatePhotoRejected(str(e))
        except NoFaceDetected: raise GateNoFaceDetected()
        except MultipleFacesDetected: raise GateMultipleFaces()
        except FaceTooSmall: raise GateFaceTooSmall()
        except FaceTooBlurry: raise GateFaceTooBlurry()
        except FaceQualityError: raise GateFaceUnusable()
        except FaceEmbedderUnavailable: raise GateModelUnavailable()
        return Response(FaceEnrollmentSerializer(_face(enrollment)).data, status=202)
    @extend_schema(parameters=[OCCUPANCY_HEADER_PARAMETER], request=None, responses={204: None})
    def delete(self, request):
        occupancy, _ = resolve_api_occupancy(request); revoke_face_enrollment(occupancy); return Response(status=204)

def _credential(request):
    try: return authenticate_device(token_from_header(request.headers.get("Authorization")), ip=client_ip(request))
    except GateCredentialRevoked: raise GateDeviceRevoked()
    except GateCredentialExpired: raise GateDeviceExpired()
    except GateAuthenticationFailed: raise GateDeviceUnauthenticated()
    except DjangoPermissionDenied: raise exceptions.Throttled()

def _outcome(o):
    return {"matched": o.matched, "display_name": o.display_name, "unit_label": o.unit_label, "direction": o.direction, "score": o.score}

def _reader(request):
    credential = _credential(request)
    if not cache.add(f"gate-recognition:{credential.device_id}", True, timeout=settings.GATE_RECOGNITION_THROTTLE_SECONDS):
        raise GateRecognitionThrottled()
    return credential


class GateDeviceView(APIView):
    authentication_classes = []; permission_classes = []
    @extend_schema(auth=[{"GateDevice": []}], responses=GateDeviceSerializer)
    def get(self, request):
        device = _credential(request).device
        return Response(GateDeviceSerializer({"label": device.label, "direction": device.direction}).data)

class GateRecognizeFaceView(APIView):
    authentication_classes = []; permission_classes = []; parser_classes = [parsers.MultiPartParser]
    @extend_schema(auth=[{"GateDevice": []}], request=FaceRecognizeSerializer, responses=RecognitionOutcomeSerializer)
    def post(self, request):
        data = FaceRecognizeSerializer(data=request.data); data.is_valid(raise_exception=True)
        if data.validated_data["photo"].size > settings.GATE_MAX_FACE_UPLOAD_BYTES: raise GateFaceUploadTooLarge()
        try: return Response(RecognitionOutcomeSerializer(_outcome(recognize_face(_reader(request), data.validated_data["photo"].read()))).data)
        except NoFaceDetected: raise GateNoFaceDetected()
        except MultipleFacesDetected: raise GateMultipleFaces()
        except FaceTooSmall: raise GateFaceTooSmall()
        except FaceTooBlurry: raise GateFaceTooBlurry()
        except FaceQualityError: raise GateFaceUnusable()
        except FaceEmbedderUnavailable: raise GateModelUnavailable()

class GateRecognizePlateView(APIView):
    authentication_classes = []; permission_classes = []
    @extend_schema(auth=[{"GateDevice": []}], request=PlateRecognizeSerializer, responses=RecognitionOutcomeSerializer)
    def post(self, request):
        data = PlateRecognizeSerializer(data=request.data); data.is_valid(raise_exception=True)
        try: outcome = recognize_plate(_reader(request), data.validated_data["plate"])
        except PlateFormatError: raise GatePlateUnreadable()
        return Response(RecognitionOutcomeSerializer(_outcome(outcome)).data)
