from django.contrib import admin
from .models import Document, DocumentVersion


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("pk", "building", "kind", "created_at")
    list_filter = ("kind", "building")


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("pk", "document", "filename", "sha256", "byte_size", "scan_status", "created_at")
    list_filter = ("scan_status", "document__kind")
    search_fields = ("filename", "sha256")
