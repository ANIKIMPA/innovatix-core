from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from innovatix.geo_territories.utils import get_default_country
from innovatix.users.constants import DEFAULT_COUNTRY_CODE, LANGUAGE_CHOICES
from innovatix.users.models.base_user import BaseUser


class AbstractCustomerUser(BaseUser):
    """
    An abstract base class for CustomerUser model.
    """

    external_customer_id = models.CharField(_("Stripe ID"), max_length=50, blank=True)
    partner_number = models.CharField(
        _("partner number"),
        max_length=20,
        unique=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{4}-\d{2}-\d{4}$",
                message=_("Partner number must be in the format: 'YYYY-MM-####'"),
                code="invalid_partner_number",
            )
        ],
    )
    accept_email_marketing = models.BooleanField(
        _("Customer agreed to receive marketing emails."), default=True
    )
    accept_sms_marketing = models.BooleanField(
        _("Customer agreed to receive SMS marketing text messages."),
        default=True,
        help_text=_(
            "You should ask your customers for permission before you subscribe them to your marketing emails or SMS."
        ),
    )
    accept_terms_condition = models.BooleanField(
        _("Customer agreed to the Terms and Conditions."),
        default=False,
    )
    address1 = models.CharField(_("address"), max_length=150)
    address2 = models.CharField(_("apartment, suite, etc."), max_length=150, blank=True)
    city = models.CharField(_("city"), max_length=75)
    province = models.ForeignKey(
        "geo_territories.Province", verbose_name=_("state"), on_delete=models.PROTECT
    )
    country = models.ForeignKey(
        "geo_territories.Country", on_delete=models.PROTECT, default=get_default_country
    )
    tags = models.ManyToManyField(
        "users.Tag",
        help_text=_("Tags can be used to categorize customers into groups."),
        blank=True,
    )
    zip = models.CharField(_("zip code"), max_length=5)
    notes = models.TextField(
        _("notes"), blank=True, help_text=_("Add notes about your customer.")
    )
    langugage = models.CharField(
        _("langugage"),
        max_length=30,
        choices=LANGUAGE_CHOICES,
        default="spanish",
    )
    pay_tax = models.BooleanField(_("Collect tax"), default=True)

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def format_phone_number(self):
        country_code = getattr(self.country, "code", DEFAULT_COUNTRY_CODE)
        return super().format_phone_number(country_code)

    def generate_partner_number(self):
        current_date = timezone.now()

        # Get the number of CustomerUser instances that were created this month
        # This uses the __year and __month field lookups to filter instances
        # based on the year and month of the date_joined field
        count = CustomerUser.objects.filter(
            date_joined__year=current_date.year,
            date_joined__month=current_date.month,
        ).count()

        # Generate the partner_number using the year, month, and count
        # We use str.zfill to pad the count with leading zeros
        return f"{current_date.year}-{str(current_date.month).zfill(2)}-{str(count + 1).zfill(4)}"

    def generate_password(self):
        # Generate a random password
        while True:
            password = get_random_string(
                length=10,
                allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()",
            )
            try:
                validate_password(password, self)
            except ValidationError:
                pass  # If the password is invalid, try again
            else:
                return password  # If the password is valid, return it

    def save(self, *args, **kwargs: str):
        # Only set the partner_number and password if this instance is being created
        if not self.pk:
            self.partner_number = self.generate_partner_number()

            password = self.generate_password()
            self.set_password(password)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if not self.get_full_name():
            return self.email

        return self.get_full_name()

    class Meta:
        abstract = True


class CustomerUser(AbstractCustomerUser):
    """
    A class implementing a fully featured CustomerUser model.
    """

    pass
