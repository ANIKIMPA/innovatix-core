from decimal import Decimal

from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from innovatix.core.forms import CoreModelForm
from payments.models import Payment, PaymentMethod


class PaymentForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    # super().__init__(*args, **kwargs)
    # self["subtotal"].initial = self.instance.get_display_subtotal()
    # self["tax"].initial = self.instance.get_display_tax()
    # self["total"].initial = self.instance.get_display_total()

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentMethodForm(CoreModelForm):
    payment_method_id = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = PaymentMethod
        fields = [
            "card_name",
        ]
