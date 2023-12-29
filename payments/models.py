from django.contrib import admin
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.templatetags.core_tags import dollar_format
from payments.constants import PAYMENT_STATUS_CHOICES


class PaymentMethod(models.Model):
    """
    Represents a payment method associated with a user.
    """

    PAYMENT_METHOD_CHOICES = [
        ("visa", "Visa"),
        ("mastercard", "MasterCard"),
        ("paypal", "PayPal"),
        ("american_express", "American Express"),
        ("discover", "Discover"),
        ("diners_club", "Diners Club"),
        ("apple_pay", "Apple Pay"),
        ("meta_pay", "Meta Pay"),
        ("google_pay", "Google Pay"),
        ("shop_pay", "Shop Pay"),
        # Add any other payment methods you accept here
    ]

    external_payment_method_id = models.CharField(
        _("stripe ID"), max_length=50, blank=True
    )
    user = models.ForeignKey(
        "users.CustomerUser", verbose_name=_("customer"), on_delete=models.CASCADE
    )
    card_name = models.CharField(_("name on card"), max_length=150)
    type = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    last_four = models.CharField(
        max_length=4, validators=[MinLengthValidator(4), MaxLengthValidator(4)]
    )
    expiration_month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    expiration_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2023)]
    )

    def get_display_card_number(self):
        return f"•••• {self.last_four}"

    def get_display_type(self):
        return [val for (key, val) in self.PAYMENT_METHOD_CHOICES if self.type == key][
            0
        ]

    def get_display_expires(self):
        return f"{self.expiration_month:02d} / {self.expiration_year}"

    def __str__(self):
        return f"{self.get_display_type()}: {self.get_display_card_number()}"

    class Meta:
        verbose_name = _("payment method")
        verbose_name_plural = _("payment methods")


class Payment(models.Model):
    """
    Represents a payment made by a user for a membership.
    """

    external_payment_id = models.CharField(_("stripe ID"), max_length=50, blank=True)
    description = models.CharField(
        _("description"), max_length=150, blank=True, null=True
    )

    user_membership = models.ForeignKey(
        "products.UserMembership",
        verbose_name=_("subscription"),
        on_delete=models.CASCADE,
        null=True,
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True
    )
    date = models.DateTimeField(_("paid on"), default=timezone.now)
    subtotal = models.IntegerField(_("subtotal"), validators=[MinValueValidator(0)])
    tax = models.IntegerField(_("tax"), validators=[MinValueValidator(0)])
    total = models.IntegerField(_("total"), validators=[MinValueValidator(0)])
    status = models.CharField(
        choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    def get_display_status(self):
        return [val for (key, val) in PAYMENT_STATUS_CHOICES if self.status == key][0]

    def get_display_subtotal(self):
        return dollar_format(self.get_subtotal())

    def get_display_tax(self):
        return dollar_format(self.get_tax())

    @admin.display(description=_("Amount"))
    def get_display_total(self):
        return dollar_format(self.get_total())

    def get_subtotal(self):
        return self.subtotal / 100

    def get_tax(self):
        return self.tax / 100

    def get_total(self):
        return self.total / 100

    def has_payment_method(self) -> bool:
        return self.payment_method is not None

    def __str__(self):
        return f"{self.get_display_total()} USD - {self.get_display_status()}"

    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")
