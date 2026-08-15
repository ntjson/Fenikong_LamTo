"""
URL configuration for config project.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from lamto.web.views.security import SecureLoginView, secure_logout

handler500 = "lamto.web.views.errors.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        SecureLoginView.as_view(template_name="web/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        secure_logout,
        name="logout",
    ),
    path("api/v1/", include("lamto.api.urls")),
    path(
        "e/<str:public_token>/",
        include("lamto.explorer.urls"),
    ),
    path("", include("lamto.web.urls")),
]
