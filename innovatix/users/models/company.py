from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from innovatix.core.services.phone_number_service import PhoneNumberService
from innovatix.geo_territories.utils import get_default_country


class Company(models.Model):
    """
    Represents a company in the system.

    Attributes:
        name (str): The name of the company.
        address (str): The address of the company.
        city (str): The city where the company is located.
        state (str): The state where the company is located.
        country (str): The country where the company is located.
        zip (str): The zip code of the company.
        phone (str): The phone number of the company.
        email (str): The email address of the company.
        website (str): The website URL of the company.
        preferences (str): The posting preferences for the company.
        description (str): The description of the company.
        is_individual (bool): Whether the record represents an individual business owner.
    """

    name = models.CharField(_("name"), max_length=255)
    address = models.CharField(_("address"), max_length=255)
    city = models.CharField(_("city"), max_length=100)
    state = models.ForeignKey(
        "geo_territories.Province",
        verbose_name=_("state"),
        on_delete=models.PROTECT,
    )
    country = models.ForeignKey(
        "geo_territories.Country",
        on_delete=models.PROTECT,
        default=get_default_country,
    )
    zip = models.CharField(_("zip code"), max_length=5)
    phone = models.CharField(
        _("phone"),
        max_length=20,
        validators=[PhoneNumberService.validate_phone_number],
    )
    email = models.EmailField(_("email"))
    website = models.URLField(_("website"), null=True, blank=True)
    is_individual = models.BooleanField(_("is individual"), default=False)
    preferences = models.TextField(_("preferences"), blank=True, default="")
    description = models.TextField(_("description"), blank=True, default="")

    def __str__(self):
        return self.name

    def save(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        self.phone = PhoneNumberService.format_phone_number(self.phone)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
