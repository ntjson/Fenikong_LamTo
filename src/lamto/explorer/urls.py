from django.urls import path, reverse

from . import views

app_name = "explorer"

urlpatterns = [
    path("", views.explorer_page, name="detail"),
    path("doc/<str:sha256>/", views.document_download, name="document-download"),
]


def explorer_public_url(public_token: str | None, request=None) -> str | None:
    """Resolve the absolute or relative Evidence explorer URL for a public token."""
    if not public_token:
        return None
    rel = reverse("explorer:detail", kwargs={"public_token": public_token})
    if request is not None:
        return request.build_absolute_uri(rel)
    return rel
