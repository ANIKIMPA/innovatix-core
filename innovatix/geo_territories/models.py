from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    """
    Represents a country.
    """

    name = models.CharField(_("name"), max_length=75, unique=True)
    code = models.CharField(_("code"), max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")
        ordering = ["name"]


class Province(models.Model):
    """
    Represents a province or state within a country.
    """

    name = models.CharField(_("name"), max_length=75, unique=True)
    code = models.CharField(_("abbreviation"), max_length=2)
    capital = models.CharField(_("capital"), max_length=75, blank=True)
    type = models.CharField(_("type"), max_length=50, blank=True)
    country = models.ForeignKey("Country", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.country.name})"

    class Meta:
        verbose_name = _("state")
        verbose_name_plural = _("states")
        ordering = ["name"]


class Address(models.Model):
    """
    Represents a address object.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    name = models.CharField(_("name"), max_length=255, blank=True)
    line1 = models.CharField(_("line 1"), max_length=255)
    line2 = models.CharField(_("line 2"), max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=255, blank=True)
    postal_code = models.CharField(_("postal code"), max_length=10)
    state = models.ForeignKey(
        Province,
        verbose_name=_("estado"),
        on_delete=models.PROTECT,
    )
    country = models.ForeignKey(
        Country,
        verbose_name=_("País"),
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.line1}, {self.city}, {self.state}, {self.country}"

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ["created_at"]
