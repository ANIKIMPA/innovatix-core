from typing import Any

from django.db.models.query import QuerySet
from django.http import Http404
from django.views.generic import DetailView
from django.views.generic.edit import FormView

from core.views import CoreListView
from products.models import Membership


class MembershipInfoView(FormView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "membership": self.membership,
                "subtotal": self.subtotal,
            }
        )
        return context


class MembershipDetailView(DetailView):
    model = Membership


class MembershipListView(CoreListView):
    model = Membership
    context_object_name = "memberships"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        return queryset.filter(is_visible=True).order_by("pk")
