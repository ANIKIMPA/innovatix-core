from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from innovatix.core.templatetags.core_tags import dollar_format
from products.constants import (
    RECURRING_INTERVAL_CHOICES,
    RECURRING_INTERVAL_TO_SPANISH,
    RECURRING_PAYMENT_INTERVAL_HELP_TEXT,
)


class Membership(models.Model):
    """
    Represents a membership that a customer can subscribe to.
    """

    external_product_id = models.CharField(_("stripe ID"), max_length=50, blank=True)
    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text=_("This field represents the unique URL for the membership."),
    )
    short_description = models.TextField(_("short description"), blank=True)
    long_description = models.TextField(_("long description"), blank=True)
    entry_cost = models.IntegerField(_("entry cost"), validators=[MinValueValidator(0)])
    recurring_price = models.IntegerField(_("price"), validators=[MinValueValidator(0)])
    recurring_payment = models.CharField(
        _("recurring interval"),
        max_length=30,
        choices=RECURRING_INTERVAL_CHOICES,
        help_text=RECURRING_PAYMENT_INTERVAL_HELP_TEXT,
    )
    is_visible = models.BooleanField(_("Show on public site"), default=True)
    is_purchasable = models.BooleanField(
        _("Purchasable"),
        help_text=_(
            "Customers can purchase this even if it is not visible in the home page."
        ),
        default=True,
    )
    created_at = models.DateTimeField(_("Created"), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("membership")
        verbose_name_plural = _("memberships")

    def delete(self, *args, **kwargs):
        if self.is_linked_to_subscriptions():
            raise ValidationError(
                "Cannot delete membership that is associated with a subscription."
            )

        super(Membership, self).delete(*args, **kwargs)

    def get_display_recurring_price(self):
        return f"{dollar_format(self.get_recurring_price())} / {RECURRING_INTERVAL_TO_SPANISH.get(self.recurring_payment)}"

    def get_display_entry_cost(self):
        return dollar_format(self.get_entry_cost())

    def get_recurring_price(self):
        return self.recurring_price / 100

    def get_entry_cost(self):
        return self.entry_cost / 100

    def get_absolute_url(self):
        return reverse("products:membership-detail", args=[str(self.slug)])

    def get_subcriptions_count(self):
        return UserMembership.objects.filter(membership=self).count()

    def is_linked_to_subscriptions(self):
        """
        Check if this membership is associated with any subscriptions
        """
        return UserMembership.objects.filter(membership=self, status="active").exists()

    def __str__(self) -> str:
        return f"{self.name} • {self.get_display_recurring_price()}"


class UserMembership(models.Model):
    """
    Represents the association between a user and a membership.
    """

    MEMBERSHIP_STATUS_CHOICES = [
        (_("trialing"), _("Trialing")),
        (_("active"), _("Active")),
        (_("past_due"), _("Past_due")),
        (_("unpaid"), _("Unpaid")),
        (_("canceled"), _("Canceled")),
        (_("incomplete"), _("Incomplete")),
        (_("incomplete_expired"), _("Incomplete_expired")),
        (_("ended"), _("Ended")),
    ]

    external_subscription_id = models.CharField(
        _("stripe ID"), max_length=50, blank=True
    )
    user = models.OneToOneField(
        "users.CustomerUser",
        verbose_name=_("customer"),
        on_delete=models.CASCADE,
    )
    membership = models.ForeignKey("Membership", on_delete=models.PROTECT)
    date_subscribed = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        _("status"),
        max_length=30,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default="active",
    )
    recurring_price = models.IntegerField(_("price"), validators=[MinValueValidator(0)])
    recurring_payment = models.CharField(
        _("recurring interval"),
        max_length=30,
        choices=RECURRING_INTERVAL_CHOICES,
        help_text=RECURRING_PAYMENT_INTERVAL_HELP_TEXT,
    )

    def get_display_recurring_price(self):
        return f"{dollar_format(self.get_recurring_price())} / {RECURRING_INTERVAL_TO_SPANISH.get(self.recurring_payment)}"

    def get_recurring_price(self):
        return self.recurring_price / 100

    def get_successful_payments(self):
        return self.payment_set.count()

    @admin.display(description=_("Next Billing Date"))
    def get_next_billing_date(self):
        if not self.membership:
            return "-"
        kwargs = {
            f"{self.membership.recurring_payment}s": self.get_successful_payments()
        }
        next_billing_date = self.date_subscribed + relativedelta(**kwargs)
        return date(next_billing_date)

    def __str__(self) -> str:
        if self.membership is not None:
            return f"{self.user.email} - {self.membership.name} • {self.get_display_recurring_price()}"

        return f"{self.user.email} - No membership"

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
