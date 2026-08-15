from django.urls import path

from . import views

app_name = "explorer"

urlpatterns = [
    path("", views.explorer_page, name="detail"),
    path("doc/<str:sha256>/", views.document_download, name="document-download"),
]
