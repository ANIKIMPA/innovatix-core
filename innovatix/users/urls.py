from django.urls import path

from innovatix.users.views import CoreContactFormView, CustomerInfoFormView

app_name = "users"

urlpatterns = [
    path("contactanos/", CoreContactFormView.as_view(), name="contact"),
    path(
        "membresias/<slug:slug>/usuario-info/",
        CustomerInfoFormView.as_view(),
        name="customer-info",
    ),
]
