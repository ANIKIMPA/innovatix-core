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
