from django.urls import path
from products.views import (
    CustomerInfoUpdateView,
    MembershipDetailView,
    MembershipListView,
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
        CustomerInfoUpdateView.as_view(),
        name="customer-info",
    ),
]
