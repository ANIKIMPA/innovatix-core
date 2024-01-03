from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """
    Represents a tag that can be associated with a customer.
    """

    text = models.CharField(_("text"), max_length=50, unique=True)
    description = models.TextField(_("description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.text} ({self.description})"

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ["text"]
