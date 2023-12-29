from django.urls import path

from payments.views import PaymentCanceledView, PaymentInfoFormView, PaymentSuccessView

app_name = "payments"

urlpatterns = [
    path(
        "membresias/<slug:slug>/pago-info/",
        PaymentInfoFormView.as_view(),
        name="payment-info",
    ),
    path(
        "pago-completado/",
        PaymentSuccessView.as_view(),
        name="payment-success",
    ),
    path(
        "pago-cancelado/",
        PaymentCanceledView.as_view(),
        name="payment-canceled",
    ),
]
