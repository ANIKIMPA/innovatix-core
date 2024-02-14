from typing import Any

from django.db.models.query import QuerySet
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import DetailView

from innovatix.core.views import CoreFormView, CoreListView
from innovatix.users.forms import CustomerUserForm
from products.models import Membership
from products.services import payment_gateway


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
    template_name = "products/customer_info_form.html"

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
