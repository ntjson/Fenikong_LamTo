"""FCM sender + payload minimization (spec 7.1, 7.4). No abstraction layer:
firebase_admin.messaging is called directly.

Event-code string literals are inlined (not imported from services) so this
module does not circular-import with services (which re-exports send_push).
"""

from django.conf import settings

# Fixed generic Vietnamese copy shown by the OS before the app runs (spec 7.4);
# never the delivery's sensitive subject/body. Keys match services.EVENT_*.
PUSH_COPY = {
    "report.receipt": ("Đã nhận phản ánh", "Phản ánh của bạn đã được ghi nhận."),
    "triage.status": ("Phản ánh đã được phân loại", "Phản ánh của bạn đã được mở thành yêu cầu xử lý."),
    "work.completed": ("Công việc đã hoàn thành", "Vui lòng đánh giá công việc đã thực hiện."),
    "ledger.publication": ("Khoản chi mới được công bố", "Có khoản chi mới trong sổ quỹ tòa nhà."),
    "building.bill_issued": ("Có hóa đơn mới từ ban quản lý", "Mở ứng dụng để xem chi tiết."),
}
_DEFAULT_COPY = ("Thông báo mới", "Bạn có một thông báo mới.")
_ANNOUNCEMENT_COPY = {
    "published": (
        "Thông báo mới từ ban quản lý",
        "Mở ứng dụng để xem nội dung.",
    ),
    "updated": (
        "Thông báo của ban quản lý đã được cập nhật",
        "Mở ứng dụng để xem nội dung mới.",
    ),
    "withdrawn": (
        "Thông báo của ban quản lý đã được thu hồi",
        "Mở ứng dụng để kiểm tra.",
    ),
}

# Allowlisted entity segment (from event_key) -> app deep-link route type.
DEEP_LINK_TYPES = {
    "report": "report",
    "case": "case",
    "entry": "ledger",
    "bill": "bill",
}

_firebase_app = None


def _ensure_app():
    global _firebase_app
    if _firebase_app is None:
        import firebase_admin
        from firebase_admin import credentials

        _firebase_app = firebase_admin.initialize_app(
            credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        )
    return _firebase_app


def send_push(token, *, title, body, data, collapse_key=None) -> str:
    """Send one FCM message; returns the provider message id. Raises firebase
    messaging errors, classified by classify_push_error."""
    from firebase_admin import messaging

    _ensure_app()
    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in data.items()},
        android=messaging.AndroidConfig(collapse_key=collapse_key) if collapse_key else None,
        apns=(
            messaging.APNSConfig(headers={"apns-collapse-id": collapse_key})
            if collapse_key
            else None
        ),
    )
    return messaging.send(message)


def classify_push_error(exc) -> str:
    """Terminal (dead token -> deactivate device) vs transient (retry) (spec 7.3).

    Terminal covers all invalid/unregistered/mismatched-token cases exposed by
    pinned firebase-admin>=6,<8: UnregisteredError, SenderIdMismatchError, and
    InvalidArgumentError for bad registration tokens. Everything else is transient.
    """
    from firebase_admin import exceptions, messaging

    if isinstance(exc, (messaging.UnregisteredError, messaging.SenderIdMismatchError)):
        return "terminal"
    # InvalidArgumentError lives on firebase_admin.exceptions (not messaging) in >=6.
    if isinstance(exc, exceptions.InvalidArgumentError):
        msg = str(exc).lower()
        if any(
            needle in msg
            for needle in (
                "registration token",
                "not a valid fcm",
                "invalid registration",
                "requested entity was not found",
            )
        ):
            return "terminal"
    return "transient"


def _parse_reference(event_key: str):
    parts = event_key.split(":")
    if len(parts) >= 3:
        return parts[1], parts[2]
    return None, None


def _event_code_from_key(event_key: str) -> str:
    """Prefix before the first ':' — same contract as services._event_code_from_key."""
    if not event_key:
        return ""
    return event_key.split(":", 1)[0]


def build_push_payload(delivery):
    """Generic Vietnamese title/body + allowlisted deep link + delivery id (spec 7.4)."""
    code = delivery.event_code or _event_code_from_key(delivery.event_key)
    if code == "building.announcement":
        title, body = _ANNOUNCEMENT_COPY.get(
            delivery.event_key.rsplit(":", 1)[-1], _DEFAULT_COPY
        )
    else:
        title, body = PUSH_COPY.get(code, _DEFAULT_COPY)
    entity, entity_id = _parse_reference(delivery.event_key)
    link_type = DEEP_LINK_TYPES.get(entity, "notifications")
    data = {"type": link_type, "id": entity_id or "", "delivery_id": str(delivery.pk)}
    return title, body, data
