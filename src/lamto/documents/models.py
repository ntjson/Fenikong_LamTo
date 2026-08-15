from django.conf import settings
from django.db import models

from lamto.accounts.models import Building


class InsertOnlyModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Document records are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Document records are append-only.")


class Document(InsertOnlyModel):
    class Kind(models.TextChoices):
        REPORT_PHOTO = "REPORT_PHOTO", "Report photo"
        BEFORE_PHOTO = "BEFORE_PHOTO", "Before photo"
        AFTER_PHOTO = "AFTER_PHOTO", "After photo"
        QUOTATION = "QUOTATION", "Quotation"
        INVOICE = "INVOICE", "Invoice"
        ACCEPTANCE_REPORT = "ACCEPTANCE_REPORT", "Completion report"
        PAYMENT_PROOF = "PAYMENT_PROOF", "Payment proof"
        CONTRACT = "CONTRACT", "Contract"
        RESIDENT_BILL = "RESIDENT_BILL", "Resident bill"

    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    kind = models.CharField(max_length=32, choices=Kind.choices)


class DocumentVersion(InsertOnlyModel):
    class ScanStatus(models.TextChoices):
        CLEAN = "CLEAN", "Clean"

    document = models.ForeignKey(Document, on_delete=models.PROTECT, related_name="versions")
    version = models.PositiveIntegerField()
    storage_key = models.CharField(max_length=512, unique=True)
    provider_version_id = models.CharField(max_length=512)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=127)
    byte_size = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64)
    scan_status = models.CharField(max_length=16, choices=ScanStatus.choices, default=ScanStatus.CLEAN)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["document", "version"], name="document_version_once")
        ]


class QuarantinedUpload(InsertOnlyModel):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    building = models.ForeignKey(
        Building,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="quarantined_uploads",
    )
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=127, blank=True)
    byte_size = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64, blank=True)
    reason = models.CharField(max_length=255)
    storage_key = models.CharField(max_length=512, blank=True, null=True, unique=True)
    provider_version_id = models.CharField(max_length=512, blank=True)
    retention_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
