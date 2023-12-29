from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from core.utils import log_creation
from core.views import CoreFormView
from products.views import MembershipInfoView
from users.forms import ContactForm, CustomerUserForm
from users.models import ContactModel


class ContactFormView(CoreFormView):
    template_name = "users/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home")

    def mail_prgun_managers(self, contact: ContactModel):
        send_mail(
            "[PR Gun Association] Nueva solicitud de contacto",
            f"Tienes una nueva solicitud de contacto de:\n\n"
            f"Nombre: {contact.name}\n"
            f"Email: {contact.email}\n"
            f"Teléfono: {contact.phone_number}\n\n"
            f"Mensaje:\n{contact.message}\n",
            contact.email,
            ["manager@example.com"],  # manager's email
        )

    def form_valid(self, form):
        contact = form.save()

        log_creation(contact)

        # self.mail_prgun_managers(instance)

        # Add a message to tell the user the email was sent
        messages.success(
            self.request, _("Your message has been sent. Thank you for contacting us.")
        )

        return super().form_valid(form)


class CustomerInfoFormView(MembershipInfoView):
    form_class = CustomerUserForm
    template_name = "users/customer_info_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Check if form data is in session
        if "user_info" in self.request.session:
            # Use session data to pre-populate form
            kwargs["initial"] = self.request.session["user_info"]

        return kwargs

    def get_success_url(self):
        # reverse_lazy with dynamic URL part
        return reverse_lazy(
            "payments:payment-info", kwargs={"slug": self.membership.slug}
        )

    def form_valid(self, form: CustomerUserForm):
        self.request.session["user_info"] = form.cleaned_data_with_model_pk()

        return super().form_valid(form)
