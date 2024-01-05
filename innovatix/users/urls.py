from django.urls import path

from innovatix.users.views import ContactFormView, CustomerInfoFormView

app_name = "users"

urlpatterns = [
    path("contactanos/", ContactFormView.as_view(), name="contact"),
    path(
        "membresias/<slug:slug>/usuario-info/",
        CustomerInfoFormView.as_view(),
        name="customer-info",
    ),
]
