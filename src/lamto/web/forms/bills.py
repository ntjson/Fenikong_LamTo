from django import forms
from django.utils.translation import gettext_lazy as _

from lamto.web.forms.fields import WholeVndField


class BillForm(forms.Form):
    resident = forms.ChoiceField(label=_("Resident"))
    title = forms.CharField(max_length=160, strip=True, label=_("Title"))
    amount_vnd = WholeVndField(label=_("Amount (VND)"))
    period = forms.CharField(
        max_length=64,
        required=False,
        strip=True,
        label=_("Period"),
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "2026-07"}),
    )
    due_date = forms.DateField(
        required=False,
        label=_("Due date"),
        widget=forms.DateInput(attrs={"type": "date", "class": "input"}),
    )
    note = forms.CharField(
        max_length=500,
        required=False,
        strip=True,
        label=_("Note"),
        widget=forms.Textarea(attrs={"class": "input", "rows": 3}),
    )
    document = forms.FileField(label=_("Bill document"))

    def __init__(self, *args, resident_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["resident"].choices = list(resident_choices)


class VoidBillForm(forms.Form):
    reason = forms.CharField(max_length=500, label=_("Reason"))
    confirm = forms.BooleanField(
        required=True,
        label=_("I understand voiding this bill cannot be undone."),
    )
