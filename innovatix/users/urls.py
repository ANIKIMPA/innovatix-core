from django.urls import path

from .views import ContactFormView

app_name = "users"

urlpatterns = [
    path("contactanos/", ContactFormView.as_view(), name="contact"),
]
