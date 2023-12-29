from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models.base_user import BaseUser, BaseUserManager


class ProgramUserManager(BaseUserManager):
    pass

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, first_name, last_name, password, **extra_fields)


class ProgramUser(BaseUser, PermissionsMixin):
    """
    An class implementing a fully featured ProgramUser model with
    admin-compliant permissions.

    Email, firstname, lastname and password are required. Other fields are optional.
    """

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    objects = ProgramUserManager()

    class Meta:
        verbose_name = _("Administrator")
        verbose_name_plural = _("Administrators")
