from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import storages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from django.utils.translation import gettext

from lamto.gate.devices import issue_credential, revoke_credential, rotate_credential
from lamto.gate.models import FaceEnrollment, GateDevice, GateDeviceCredential, GateEvent, PendingEnrollmentPhoto, ReviewStatus, VehiclePlate
from lamto.gate.review import approve_face, approve_plate, reject_face, reject_plate, revoke_face, revoke_plate_as_manager, ReviewNotPossible
from lamto.web.staff import require_management_context, staff_context

def _context(request, membership, memberships, **extra):
    return staff_context(request, membership, memberships, nav_active="gate", **extra)

@login_required
@require_GET
def gate_queue(request):
    membership, memberships = require_management_context(request)
    return render(request, "web/staff/gate_queue.html", _context(request, membership, memberships, gate_active="review",
        pending_faces=FaceEnrollment.objects.filter(status=ReviewStatus.PENDING, occupancy__unit__building=membership.building).select_related("occupancy__user", "occupancy__unit"),
        pending_plates=VehiclePlate.objects.filter(status=ReviewStatus.PENDING, building=membership.building).select_related("occupancy__user", "occupancy__unit")))

@login_required
@require_GET
def gate_face_photo(request, pk):
    membership, _ = require_management_context(request)
    photo = get_object_or_404(PendingEnrollmentPhoto, enrollment_id=pk, enrollment__occupancy__unit__building=membership.building)
    try: handle = storages["private"].open(photo.storage_key, "rb")
    except (FileNotFoundError, OSError) as error: raise Http404 from error
    response = FileResponse(handle, content_type=photo.content_type)
    response["Cache-Control"] = "private, no-store"
    response["Pragma"] = "no-cache"
    return response

@login_required
@require_http_methods(["POST"])
def gate_face_decide(request, pk):
    membership, _ = require_management_context(request); enrollment = get_object_or_404(FaceEnrollment, pk=pk, occupancy__unit__building=membership.building)
    try:
        decision = request.POST.get("decision")
        if decision == "approve":
            approve_face(enrollment, membership)
            messages.success(request, gettext("Face enrolment for %(name)s approved.") % {"name": enrollment.occupancy.user.display_name})
        elif decision == "reject":
            reject_face(enrollment, membership, request.POST.get("note", ""))
            messages.success(request, gettext("Face enrolment for %(name)s rejected.") % {"name": enrollment.occupancy.user.display_name})
        elif decision == "revoke":
            if request.POST.get("confirm") != "1":
                messages.error(request, gettext("Tick the confirmation box to revoke. Nothing was changed."))
            else:
                name = enrollment.occupancy.user.display_name
                revoke_face(enrollment, membership)
                messages.success(request, gettext("Face access for %(name)s is revoked; the stored face data is deleted.") % {"name": name})
        else: messages.error(request, gettext("Unknown decision."))
    except ReviewNotPossible as error: messages.error(request, str(error))
    return redirect(request.POST.get("next") or "web:gate-queue")

@login_required
@require_http_methods(["POST"])
def gate_plate_decide(request, pk):
    membership, _ = require_management_context(request); plate = get_object_or_404(VehiclePlate, pk=pk, building=membership.building)
    try:
        decision = request.POST.get("decision")
        if decision == "approve":
            approve_plate(plate, membership)
            messages.success(request, gettext("Plate %(plate)s approved.") % {"plate": plate.plate})
        elif decision == "reject":
            reject_plate(plate, membership, request.POST.get("note", ""))
            messages.success(request, gettext("Plate %(plate)s rejected.") % {"plate": plate.plate})
        elif decision == "revoke":
            if request.POST.get("confirm") != "1":
                messages.error(request, gettext("Tick the confirmation box to revoke. Nothing was changed."))
            else:
                revoke_plate_as_manager(plate, membership)
                messages.success(request, gettext("Gate access for plate %(plate)s is revoked.") % {"plate": plate.plate})
        else: messages.error(request, gettext("Unknown decision."))
    except ReviewNotPossible as error: messages.error(request, str(error))
    return redirect(request.POST.get("next") or "web:gate-queue")

@login_required
@require_GET
def gate_registrations(request):
    membership, memberships = require_management_context(request)
    return render(request, "web/staff/gate_registrations.html", _context(request, membership, memberships, gate_active="registrations",
        faces=FaceEnrollment.objects.filter(status=ReviewStatus.APPROVED, occupancy__unit__building=membership.building).select_related("occupancy__user", "occupancy__unit"),
        plates=VehiclePlate.objects.filter(status=ReviewStatus.APPROVED, building=membership.building).select_related("occupancy__user", "occupancy__unit")))

_ISSUED_TOKEN_SESSION_KEY = "gate_devices.issued_token"

@login_required
@require_http_methods(["GET", "POST"])
def gate_devices(request):
    membership, memberships = require_management_context(request)
    if request.method == "POST":
        action = request.POST.get("action"); issued_token = None
        if action == "create":
            label = request.POST.get("label", "").strip()
            direction = request.POST.get("direction")
            if not label or direction not in GateDevice.Direction.values:
                messages.error(request, gettext("Enter a reader label and select a valid direction."))
            else:
                device = GateDevice.objects.create(building=membership.building, label=label, direction=direction)
                _cred, issued_token = issue_credential(device, membership)
                messages.success(request, gettext("Reader %(label)s registered. Configure it with the one-time credential below.") % {"label": label})
        elif action == "rotate":
            _cred, issued_token = rotate_credential(get_object_or_404(GateDevice, pk=request.POST.get("device"), building=membership.building), membership)
            messages.success(request, gettext("Credential rotated. Configure the reader with the new one-time credential below."))
        elif action == "revoke":
            if request.POST.get("confirm") != "1":
                messages.error(request, gettext("Tick the confirmation box to revoke. Nothing was changed."))
            else:
                revoke_credential(get_object_or_404(GateDeviceCredential, pk=request.POST.get("credential"), device__building=membership.building), membership)
                messages.success(request, gettext("Reader credential revoked. The reader stops authenticating immediately."))
        if issued_token:
            request.session[_ISSUED_TOKEN_SESSION_KEY] = issued_token  # one-shot: popped by the GET after redirect
        return redirect("web:gate-devices")
    return render(request, "web/staff/gate_devices.html", _context(request, membership, memberships, gate_active="devices", devices=GateDevice.objects.filter(building=membership.building).prefetch_related("credentials"), directions=GateDevice.Direction.choices, issued_token=request.session.pop(_ISSUED_TOKEN_SESSION_KEY, None)))

@login_required
@require_GET
def gate_log(request):
    membership, memberships = require_management_context(request)
    events = list(GateEvent.objects.filter(building=membership.building).select_related("device", "matched_occupancy__user", "matched_occupancy__unit").order_by("-occurred_at")[:500])
    return render(request, "web/staff/gate_log.html", _context(request, membership, memberships, gate_active="activity", events=events, events_capped=len(events) == 500))
