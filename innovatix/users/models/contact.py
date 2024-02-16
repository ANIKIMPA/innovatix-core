from typing import Any

from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _

from innovatix.core.services.phone_number_service import PhoneNumberService


class ContactModel(models.Model):
    name = models.CharField(_("full name"), max_length=75)
    email = models.EmailField(_("email address"), max_length=100)
    phone_number = models.CharField(
        _("phone number"),
        validators=[PhoneNumberService.validate_phone_number],
        max_length=17,
    )
    message = models.TextField(_("message"))

    def email_contact(
        self,
        subject: str,
        message: str,
        from_email: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Send an email to this contact."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"

    def save(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        self.phone_number = PhoneNumberService.format_phone_number(self.phone_number)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ["name"]
