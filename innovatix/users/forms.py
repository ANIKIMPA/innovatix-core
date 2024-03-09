from typing import Any

from allauth.account.forms import LoginForm, SignupForm
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from innovatix.core.forms import CoreModelForm
from innovatix.core.services import payment_gateway
from innovatix.users.models import ContactModel, CustomerUser


class ContactForm(CoreModelForm):
    class Meta:
        model = ContactModel
        fields = [
            "name",
            "email",
            "phone_number",
            "message",
        ]


# This is a custom form for creating a new customer.
# It inherits from Django's built-in UserCreationForm, which is designed
# to handle the creation of new users, including creating a hashed password.
#
# However, in this case, we don't want to require a password when creating
# a new customer. This is because initially, customers won't have access
# to an account.
#
# Despite this, we are still handling the possibility of them having access
# in the future. To do this, we are generating a random password automatically
# in the model's save method for the Customer class. This class inherits from
# Django's 'AbstractBaseUser', which includes password handling.
#
# The reason we are still handling passwords in this way is to simplify
# the development process for adding a login feature in the future.
# This way, we don't need to create a whole new Customer model without a password.
#
# If the day comes that we want to let customers have access to their accounts,
# we can simply remove this form and use Django's built-in authentication forms.
class CustomerUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password1"].help_text = ""
        self.fields["password2"].required = False
        self.fields["password2"].help_text = ""


class CustomerUserChangeForm(UserChangeForm):
    def save(self, commit: bool = True):
        """
        Save the instance first to prevent duplicate key value,
        then call the payment gateway API to create the customer there.
        """
        instance = super().save(commit)
        payment_gateway.update_customer(instance)

        return instance


class CustomerUserForm(CoreModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["accept_terms_condition"].required = True

    class Meta:
        model = CustomerUser
        fields = [
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "address1",
            "address2",
            "city",
            "country",
            "province",
            "zip",
            "accept_terms_condition",
        ]


class CompanyAddForm(ModelForm):

    def __init__(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.fields["preferences"].initial = (
            "Frecuencia (e.g. 'Diario', 'Dos veces por semana'): \n\nDías de la semana: \n\nHorario: "
        )


class CustomerLoginForm(LoginForm):
    def __init__(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs[
            "class"
        ] = "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-600"

        self.fields["password"].widget.attrs[
            "class"
        ] = "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-600"


class CustomerSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs[
            "class"
        ] = "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-600"
        self.fields["email"].help_text = _(
            "Después de someter, se enviará un correo electrónico de validación para verificar su correo electrónico."
        )

        self.fields["password1"].widget.attrs[
            "class"
        ] = "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-600"

        self.fields["password2"].widget.attrs[
            "class"
        ] = "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-600"
