from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from innovatix.geo_territories.models import Country, Province
from innovatix.geo_territories.utils import get_default_country
from innovatix.users.constants import DEFAULT_COUNTRY_CODE, LANGUAGE_CHOICES

from .base_user import BaseUser, BaseUserManager
from .company import Company


class CustomerUserManager(BaseUserManager):
    """
    Custom manager for CustomerUser model.
    """

    def create_or_update_customer_user(
        self,
        province: Province,
        country: Country,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None = None,
        **extra_fields: dict[str, Any],
    ) -> tuple["BaseUser", bool]:
        return self._create_or_update_user(
            email,
            first_name,
            last_name,
            password,
            province=province,
            country=country,
            **extra_fields,
        )


class AbstractCustomerUser(BaseUser):
    """
    An abstract base class for CustomerUser model.
    """

    external_customer_id = models.CharField(
        _("ID de Stripe"), max_length=50, blank=True
    )
    partner_number = models.CharField(
        _("número de socio"),
        max_length=20,
        unique=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{4}-\d{2}-\d{4}$",
                message=_(
                    "El número de socio debe estar en el formato: 'YYYY-MM-####'"
                ),
                code="invalid_partner_number",
            )
        ],
    )
    accept_email_marketing = models.BooleanField(
        _("Cliente aceptó recibir correos electrónicos de marketing."), default=True
    )
    accept_sms_marketing = models.BooleanField(
        _("Cliente aceptó recibir mensajes de texto de marketing por SMS."),
        default=True,
        help_text=_(
            "Debes pedir permiso a tus clientes antes de suscribirlos a tus correos electrónicos o mensajes de texto de marketing."
        ),
    )
    accept_terms_condition = models.BooleanField(
        _("Cliente aceptó los Términos y Condiciones."),
        default=False,
    )
    address1 = models.CharField(_("dirección"), max_length=150)
    address2 = models.CharField(
        _("apartamento, suite, etc."), max_length=150, blank=True
    )
    city = models.CharField(_("ciudad"), max_length=75)
    company = models.ForeignKey(
        Company,
        verbose_name=_("compañía"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    province = models.ForeignKey(
        "geo_territories.Province", verbose_name=_("estado"), on_delete=models.PROTECT
    )
    country = models.ForeignKey(
        "geo_territories.Country",
        verbose_name=_("País"),
        on_delete=models.PROTECT,
        default=get_default_country,
    )
    tags = models.ManyToManyField(
        "users.Tag",
        help_text=_(
            "Las etiquetas se pueden usar para categorizar a los clientes en grupos."
        ),
        blank=True,
    )
    zip = models.CharField(_("código postal"), max_length=5)
    notes = models.TextField(
        _("notas"), blank=True, help_text=_("Agrega notas sobre tu cliente.")
    )
    langugage = models.CharField(
        _("idioma"),
        max_length=30,
        choices=LANGUAGE_CHOICES,
        default="spanish",
    )
    pay_tax = models.BooleanField(_("Recolectar impuesto"), default=True)

    objects = CustomerUserManager()

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
