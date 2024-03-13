from typing import Any

from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from innovatix.core.views import CoreListView
from innovatix.users.forms import CustomerInfoForm
from innovatix.users.models import CustomerUser
from products.models import Membership
from products.services import payment_gateway


class MembershipInfoMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.membership: Membership = Membership.objects.get(
                slug=kwargs["slug"], is_purchasable=True
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


@method_decorator(login_required, name="dispatch")
class CustomerInfoUpdateView(MembershipInfoMixin, UpdateView):
    model = CustomerUser
    form_class = CustomerInfoForm
    template_name = "products/customeruser_update_form.html"

    def get_success_url(self):
        # reverse_lazy with dynamic URL part
        return reverse_lazy(
            "payments:payment-info", kwargs={"slug": self.membership.slug}
        )

    def get_object(self, queryset: QuerySet[CustomerUser] | None = None):
        return self.request.user


class MembershipDetailView(DetailView):
    model = Membership


class MembershipListView(CoreListView):
    model = Membership
    context_object_name = "memberships"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        return queryset.filter(is_visible=True).order_by("pk")
