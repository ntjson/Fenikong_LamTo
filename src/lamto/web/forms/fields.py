"""Form fields shared across the Management workspace."""

from __future__ import annotations

import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

WHOLE_NUMBER = re.compile(r"-?\d+")


class WholeVndField(forms.IntegerField):
    """A money amount, entered as whole đồng with no separators.

    ``IntegerField`` strips a trailing ``.0*`` before converting, so it
    accepts "460.000000" and quietly cleans it to 460. A dot is the ordinary
    Vietnamese thousands separator, and a number input keeps the first dot,
    so a manager typing 460.000.000 files a 460 đồng amount that reads as
    deliberate everywhere downstream. Refuse it rather than reinterpret it —
    an amount nobody meant is worse than an amount nobody entered.

    The check has to live on the server: a number input validates the parsed
    number, and 460.000000 is a whole 460, so no combination of ``step`` or
    ``min`` stops the browser sending it.
    """

    default_error_messages = {
        "not_whole": _("Enter the amount in whole VND, with no separators."),
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("min_value", 1)
        kwargs.setdefault("widget", forms.NumberInput(attrs={"class": "input"}))
        super().__init__(**kwargs)
        self.widget.attrs.setdefault("step", "1")
        self.widget.attrs.setdefault("inputmode", "numeric")

    def to_python(self, value):
        if value not in self.empty_values and not WHOLE_NUMBER.fullmatch(str(value).strip()):
            raise ValidationError(self.error_messages["not_whole"], code="not_whole")
        return super().to_python(value)
