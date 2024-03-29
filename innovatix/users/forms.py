from typing import Any

from allauth.account.forms import LoginForm, SignupForm
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
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


class CustomerInfoForm(CoreModelForm):
    def __init__(self, *args: Any, **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs)
        self.fields["accept_terms_condition"].required = True
        self.fields["email"].widget.attrs["readonly"] = True

    def clean_accept_terms_condition(self):
        accept_terms_condition = self.cleaned_data.get("accept_terms_condition")
        if not accept_terms_condition:
            raise ValidationError(_("Debe aceptar los términos y condiciones."))
        return accept_terms_condition

    def clean(self):
        cleaned_data = super().clean()

        if not self.instance:
            return cleaned_data

        cleaned_data["email"] = self.instance.email

        if self.instance.has_active_subscriptions():
            raise ValidationError(
                _(
                    "Ya tienes una suscripción activa. Contáctanos si deseas hacer cambios."
                )
            )

        return cleaned_data

    def save(self, commit: bool = True):
        external_customer = payment_gateway.update_customer(self.instance)
        self.instance.external_customer_id = external_customer.id

        return super().save(commit)

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
        self.fields[
            "description"
        ].initial = """
        Categoría de empresa: [Inserte aquí la categoría de empresa, por ejemplo, tecnología, moda, atención médica, etc.]

        Información básica:
        1. Productos/servicios clave: [enumere brevemente los productos o servicios clave]
        2. Público objetivo: [Describa el público objetivo: grupo de edad, intereses, ubicación geográfica, etc.]
        3. Mensaje central: [Inserte un mensaje o tema clave que desee transmitir, por ejemplo, innovación, sostenibilidad, lujo, asequibilidad, etc.]

        Aspectos destacados recientes (opcional):
        - [Cualquier logro reciente, lanzamiento de producto, evento o noticia relacionada con la empresa]

        Instrucciones especiales (opcional):
        - [Cualquier requisito específico para la publicación: tono, estilo, llamado a la acción, etc.]
        """


class AccountLoginForm(LoginForm):
    def __init__(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        print("Aqui en AccountLoginForm")
        self.fields["login"].widget.attrs[
            "class"
        ] = "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-600"

        self.fields["password"].widget.attrs[
            "class"
        ] = "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-purple-600"


class AccountSignupForm(SignupForm):
    def __init__(self, *args: Any, **kwargs: dict[str, Any]):
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
