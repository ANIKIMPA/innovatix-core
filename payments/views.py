from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from innovatix.core.views import CoreTemplateView
from innovatix.geo_territories.models import Country, Province
from innovatix.users.forms import CoreCustomerUserForm
from innovatix.users.models import CustomerUser
from payments.constants import SUCCEEDED
from payments.forms import PaymentMethodForm
from products.services import payment_gateway
from products.views import MembershipInfoView


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class PaymentCanceledView(CoreTemplateView):
    template_name = "payments/cancel.html"


class PaymentSuccessView(CoreTemplateView):
    template_name = "payments/success.html"


class PaymentInfoFormView(MembershipInfoView):
    form_class = PaymentMethodForm
    template_name = "payments/payment_info_form.html"
    success_url = reverse_lazy("payments:payment-success")

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            if "user_info" not in request.session:
                reverse("users:customer-info", args=[str(self.membership.slug)])

            self.user_info: dict = request.session.get("user_info").copy()
            self.user_info["country"] = Country.objects.get(
                pk=self.user_info.get("country")
            )
            self.user_info["province"] = Province.objects.get(
                pk=self.user_info.get("province")
            )
        except Country.DoesNotExist:
            raise Http404("No Country matches the given query.")
        except Province.DoesNotExist:
            raise Http404("No Province matches the given query.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "user_info": self.user_info,
                "pg_public_key": settings.STRIPE_PUBLIC_KEY,
            }
        )
        return context

    def form_valid(self, form):
        payment_method_id = form.cleaned_data["payment_method_id"]

        # Validate the data in the session.
        customer_form = CoreCustomerUserForm(self.user_info)
        if not customer_form.is_valid():
            return redirect("users:customer-info", slug=str(self.membership.slug))

        customer = payment_gateway.create_customer(
            CustomerUser(**self.user_info), payment_method_id=payment_method_id
        )

        payment_response = payment_gateway.create_confirm_subscription(
            customer_id=customer.id,
            payment_method_id=payment_method_id,
            membership=self.membership,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT"),
        )

        if payment_response["code"] == SUCCEEDED:
            return super().form_valid(form)
        elif payment_response["code"] == "requires_action":
            # Redirect to the same page with the client_secret as a URL parameter
            return redirect(
                f'{self.request.path}?client_secret={payment_response["client_secret"]}'
            )

        if customer.id:
            payment_gateway.delete_customer(customer.id)

        form.add_error(None, payment_response["error"]["message"])
        return self.form_invalid(form)
