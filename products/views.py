import logging
from typing import Any

from django.db.models.query import QuerySet
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

from innovatix.core.views import CoreFormView, CoreListView
from innovatix.users.forms import CustomerUserForm
from innovatix.users.webhook import handle_customer_creation, handle_customer_update
from payments.webhook import (
    handle_payment_creation,
    handle_payment_method_creation,
    handle_payment_update,
)
from products.models import Membership
from products.services import payment_gateway
from products.webhook import (
    handle_product_deleted,
    handle_subscription_creation,
    handle_subscription_update,
)

logger = logging.getLogger(__name__)


class MembershipInfoView(CoreFormView):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.membership: Membership = Membership.objects.get(
                slug=kwargs["slug"], is_visible=True
            )
        except Membership.DoesNotExist:
            raise Http404("No Membership matches the given query.")
        self.subtotal: int = (
            self.membership.recurring_price + self.membership.entry_cost
        )
        self.service_fee = payment_gateway.calculate_service_fee(
            self.membership.entry_cost
        ) + payment_gateway.calculate_service_fee(self.membership.recurring_price)
        self.total = self.subtotal + self.service_fee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "membership": self.membership,
                "subtotal": self.subtotal,
                "service_fee": self.service_fee,
                "total": self.total,
            }
        )
        return context


class CustomerInfoFormView(MembershipInfoView):
    form_class = CustomerUserForm
    template_name = "site/customer_info_form.html"

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


class MembershipDetailView(DetailView):
    model = Membership


class MembershipListView(CoreListView):
    model = Membership
    context_object_name = "memberships"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        return queryset.filter(is_visible=True).order_by("pk")


@csrf_exempt
def webhook_received(request):
    payload = request.body
    event = None

    try:
        event = payment_gateway.construct_event(payload)
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(status=400)

    # Handle the event
    if event.type == "customer.created":
        handle_customer_creation(event)
    elif event.type == "customer.updated":
        handle_customer_update(event)
    elif event.type == "invoiceitem.created":
        pass
        # print("invoiceitem.created")
    elif event.type == "payment_intent.created":
        pass
        # print("payment_intent.created")
    elif event.type == "invoice.created":
        pass
        # print("invoice.created")
    elif event.type == "invoice.finalized":
        pass
    elif event.type == "customer.subscription.created":
        handle_subscription_creation(event)
    elif event.type == "invoiceitem.updated":
        pass
    elif event.type == "charge.succeeded":
        pass
    elif event.type == "payment_method.attached":
        pass
        # print("charge.succeeded")
        # print("invoice.updated")
        # print("invoice.finalized")
    elif event.type == "product.deleted":
        handle_product_deleted(event)
    elif event.type == "invoice.updated":
        pass
    elif event.type == "invoice.paid":
        pass
        # print("invoice.paid")
    elif event.type == "invoice.payment_succeeded":
        handle_payment_creation(event)
    elif event.type == "customer.subscription.updated":
        handle_subscription_update(event)
    elif event.type == "payment_intent.succeeded":
        handle_payment_method_creation(event)
        handle_payment_update(event)
    else:
        logger.info(f"Unhandled event type {event.type}")
        return JsonResponse(
            {"status": "success", "message": "Unhandled event type"}, status=200
        )

    # Passed signature verification
    return HttpResponse(status=200)
