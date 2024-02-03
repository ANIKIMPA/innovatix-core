from django.urls import path

from products.views import (
    CustomerInfoFormView,
    MembershipDetailView,
    MembershipListView,
    webhook_received,
)

app_name = "products"
urlpatterns = [
    path("membresias/", MembershipListView.as_view(), name="membership-list"),
    path(
        "membresias/<slug:slug>",
        MembershipDetailView.as_view(),
        name="membership-detail",
    ),
    path(
        "membresias/<slug:slug>/usuario-info/",
        CustomerInfoFormView.as_view(),
        name="customer-info",
    ),
    path(
        "webhooks/stripe/",
        webhook_received,
        name="stripe-webhook",
    ),
]
