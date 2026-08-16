from django.db import models
from django.utils.translation import gettext_lazy as _

from lamto.accounts.models import Building, ManagementMembership
from lamto.maintenance.models import MaintenanceCase


class PricePrediction(models.Model):
    """A generated price band prediction or fallback recorded at comparison time."""

    class Source(models.TextChoices):
        PREDICTED = "predicted", _("Predicted")
        FALLBACK = "fallback", _("Fallback")

    building = models.ForeignKey(
        Building,
        on_delete=models.PROTECT,
        related_name="price_predictions",
    )
    case = models.ForeignKey(
        MaintenanceCase,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="price_predictions",
    )
    category = models.CharField(max_length=64)
    amount_vnd = models.BigIntegerField()
    minimum_vnd = models.BigIntegerField()
    central_vnd = models.BigIntegerField()
    maximum_vnd = models.BigIntegerField()
    reasoning = models.TextField()
    source = models.CharField(
        max_length=32,
        choices=Source.choices,
        default=Source.PREDICTED,
    )
    requested_by = models.ForeignKey(
        ManagementMembership,
        on_delete=models.PROTECT,
        related_name="price_predictions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_vnd__gt=0),
                name="price_prediction_amount_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(minimum_vnd__gt=0, central_vnd__gt=0, maximum_vnd__gt=0),
                name="price_prediction_band_positive",
            ),
        ]
