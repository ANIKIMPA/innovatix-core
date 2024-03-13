import logging
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from innovatix.core.views import CoreTemplateView
from innovatix.users.forms import CustomerInfoForm
from payments.constants import SUCCEEDED
from payments.forms import PaymentMethodForm
from products.services import payment_gateway
from products.views import MembershipInfoMixin

logger = logging.getLogger("django")


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


class PaymentInfoFormView(MembershipInfoMixin, FormView):
    form_class = PaymentMethodForm
    template_name = "payments/payment_info_form.html"
    success_url = reverse_lazy("payments:payment-success")

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: dict[str, Any]
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
        if not request.user.is_authenticated:
            login_url = reverse("account_login")
            next_url = reverse(
                "products:customer-info", args=[str(self.membership.slug)]
            )
            redirect_url = f"{login_url}?next={next_url}"
            return redirect(redirect_url)

        if not request.user.external_customer_id:
            return redirect("products:customer-info", slug=str(self.membership.slug))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "pg_public_key": settings.STRIPE_PUBLIC_KEY,
            }
        )
        return context

    def form_valid(
        self, form: PaymentMethodForm
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
        payment_method_id: str = form.cleaned_data["payment_method_id"]

        try:
            payment_response = payment_gateway.create_confirm_subscription(
                customer_id=self.request.user.external_customer_id,
                payment_method_id=payment_method_id,
                membership=self.membership,
                ip_address=get_client_ip(self.request),
                user_agent=self.request.META.get("HTTP_USER_AGENT"),
            )
        except payment_gateway.stripe.CardError as err:
            logger.error(
                f"Card error: {getattr(err, 'user_message', 'An error occurred')}"
            )
            payment_response = {
                "status": getattr(err, "http_status", 400),
                "client_secret": None,
                "message": getattr(err, "user_message", "An error occurred"),
                "code": getattr(err, "code", "card_error"),
                "error": {"message": getattr(err, "user_message", "An error occurred")},
            }
        except Exception as err:
            payment_response = {
                "status": getattr(err, "http_status", 500),
                "client_secret": None,
                "message": str(err),
                "code": getattr(err, "code", "internal_error"),
                "error": {
                    "message": _(
                        "There was an error processing your payment. Try again later."
                    )
                },
            }

        if payment_response["code"] == SUCCEEDED:
            return super().form_valid(form)
        elif payment_response["code"] == "requires_action":
            # Redirect to the same page with the client_secret as a URL parameter
            return redirect(
                f'{self.request.path}?client_secret={payment_response["client_secret"]}'
            )

        form.add_error(None, payment_response["error"]["message"])
        return self.form_invalid(form)
