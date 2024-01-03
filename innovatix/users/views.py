from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from innovatix.core.utils import log_creation
from innovatix.core.views import CoreFormView
from innovatix.users.forms import ContactForm
from innovatix.users.models import CoreContactModel


class CoreContactFormView(CoreFormView):
    template_name = "users/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home")

    def mail_managers(self, contact: CoreContactModel):
        send_mail(
            "[Innovatix Digital] Nueva solicitud de contacto",
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

        # self.mail_managers(instance)

        # Add a message to tell the user the email was sent
        messages.success(
            self.request, _("Your message has been sent. Thank you for contacting us.")
        )

        return super().form_valid(form)
