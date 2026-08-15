from django import forms
from django.utils.translation import gettext_lazy as _


class AnnouncementForm(forms.Form):
    title = forms.CharField(
        max_length=160,
        strip=True,
        label=_("Title"),
        widget=forms.TextInput(attrs={"class": "input"}),
    )
    body = forms.CharField(
        max_length=2000,
        strip=True,
        label=_("Body"),
        widget=forms.Textarea(attrs={"class": "input", "rows": 6}),
    )
    expected_revision = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
