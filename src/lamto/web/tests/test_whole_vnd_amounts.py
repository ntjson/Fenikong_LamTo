"""VND amounts are whole đồng, and a mistyped separator is refused.

A dot is the ordinary Vietnamese thousands separator. A number input keeps
the first one, and ``IntegerField`` strips a trailing ``.0*``, so "460.000.000"
used to clean silently to 460 — a real amount nobody entered, indistinguishable
downstream from a deliberate one.
"""

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from lamto.web.forms.bills import BillForm
from lamto.web.forms.fields import WholeVndField
from lamto.web.forms.staff import CreateProposalForm


class WholeVndFieldTests(SimpleTestCase):
    def test_thousands_separator_is_refused_not_truncated(self):
        field = WholeVndField()
        with self.assertRaises(ValidationError) as caught:
            field.clean("460.000000")
        self.assertEqual(caught.exception.error_list[0].code, "not_whole")

    def test_whole_amount_is_accepted(self):
        self.assertEqual(WholeVndField().clean("460000000"), 460000000)

    def test_zero_and_negative_amounts_are_still_refused(self):
        for value in ("0", "-1"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                WholeVndField().clean(value)

    def test_widget_asks_the_keyboard_for_whole_numbers(self):
        attrs = WholeVndField().widget.attrs
        self.assertEqual(attrs["step"], "1")
        self.assertEqual(attrs["inputmode"], "numeric")


class AmountFormTests(SimpleTestCase):
    def test_proposal_amount_rejects_a_separated_figure(self):
        form = CreateProposalForm(data={"amount_vnd": "460.000.000", "contractor_name": "X"})
        self.assertFalse(form.is_valid())
        self.assertIn("amount_vnd", form.errors)

    def test_proposal_amount_rejects_the_figure_the_browser_would_send(self):
        form = CreateProposalForm(data={"amount_vnd": "460.000000", "contractor_name": "X"})
        self.assertFalse(form.is_valid())
        self.assertIn("amount_vnd", form.errors)

    def test_bill_amount_rejects_a_separated_figure(self):
        form = BillForm(data={"amount_vnd": "1.500000", "title": "Phí", "resident": "1"})
        self.assertFalse(form.is_valid())
        self.assertIn("amount_vnd", form.errors)
