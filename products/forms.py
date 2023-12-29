from decimal import Decimal

from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from core.services import payment_gateway
from products.constants import (
    ENTRY_COST_HELP_TEXT,
    RECURRING_INTERVAL_CHOICES,
    RECURRING_PAYMENT_INTERVAL_HELP_TEXT,
    RECURRING_PRICE_HELP_TEXT,
)
from products.models import Membership


class MembershipBaseForm(forms.ModelForm):
    entry_cost = forms.DecimalField(
        label=_("Entry cost"),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=ENTRY_COST_HELP_TEXT,
    )
    recurring_price = forms.DecimalField(
        label=_("Price"),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=RECURRING_PRICE_HELP_TEXT,
    )

    def save(self, commit=True):
        self.instance.entry_cost = int(Decimal(self.data["entry_cost"]) * 100)
        self.instance.recurring_price = int(Decimal(self.data["recurring_price"]) * 100)

        return super().save(commit)

    class Meta:
        model = Membership
        fields = "__all__"


class MembershipAddForm(MembershipBaseForm):
    def save(self, commit=True):
        product = payment_gateway.create_membership(self.instance)
        self.instance.external_product_id = product.id

        return super().save(commit)


class MembershipChangeForm(forms.ModelForm):
    def save(self, commit=True):
        product = payment_gateway.update_membership(self.instance)
        self.instance.external_product_id = product.id

        return super().save(commit)

    class Meta:
        model = Membership
        fields = "__all__"


class MembershipPriceChangeForm(MembershipBaseForm):
    """
    A form used to change the prices of a membership in the admin interface.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["entry_cost"].initial = self.instance.get_entry_cost()
        self["recurring_price"].initial = self.instance.get_recurring_price()

    class Meta:
        model = Membership
        fields = (
            "entry_cost",
            "recurring_price",
            "recurring_payment",
        )


class UpdateSubscriptionPriceForm(forms.Form):
    new_price = forms.DecimalField(
        label=_("Price"),
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=RECURRING_PRICE_HELP_TEXT,
    )
    new_interval = forms.ChoiceField(
        label=_("Recurring interval"),
        choices=[("", "---------")] + RECURRING_INTERVAL_CHOICES,
        help_text=RECURRING_PAYMENT_INTERVAL_HELP_TEXT,
    )
