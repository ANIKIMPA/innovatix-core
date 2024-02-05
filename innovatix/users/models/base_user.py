from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from innovatix.core.services.phone_number_service import PhoneNumberService
from innovatix.users.constants import DEFAULT_COUNTRY_CODE


class BaseUserManager(UserManager):
    pass

    def _create_user(self, email, first_name, last_name, password, **extra_fields):
        """
        Create and save a user with the given email, first name, last name and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        if not first_name:
            raise ValueError("The first name must be provided")
        if not last_name:
            raise ValueError("The last name must be provided")

        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        return self._create_user(email, first_name, last_name, password, **extra_fields)


class BaseUser(AbstractBaseUser):
    """
    An abstract base class implementing a fully featured BaseUser model.

    Email, firstname, lastname and password are required. Other fields are optional.
    """

    email = models.EmailField(
        _("email"),
        max_length=150,
        unique=True,
        help_text=_("Requerido. 150 caracteres o menos."),
        error_messages={
            "unique": _("Un usuario con ese email ya existe."),
        },
    )
    first_name = models.CharField(_("nombre"), max_length=72)
    last_name = models.CharField(_("apellido"), max_length=72)
    phone_number = models.CharField(
        _("Teléfono"),
        max_length=17,
        blank=True,
        validators=[PhoneNumberService.validate_phone_number],
    )
    is_active = models.BooleanField(
        _("activo"),
        default=True,
        help_text=_(
            "Designa si este usuario debe ser tratado como activo. "
            "Anule la selección en lugar de eliminar cuentas."
        ),
    )
    date_joined = models.DateTimeField(_("fecha de registro"), default=timezone.now)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("usuario")
        verbose_name_plural = _("usuarios")
        abstract = True

    def format_phone_number(self, country_code=DEFAULT_COUNTRY_CODE):
        if not self.phone_number:
            return self.phone_number

        return PhoneNumberService.format_phone_number(self.phone_number, country_code)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self) -> str:
        return self.get_full_name()

    def save(self, *args, **kwargs):
        self.phone_number = self.format_phone_number()
        super().save(*args, **kwargs)
