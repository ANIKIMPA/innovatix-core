import logging

import stripe
from innovatix.users.models import CustomerUser
from payments.models import Payment, PaymentMethod
from products.models import UserMembership

logger = logging.getLogger("django")


def handle_payment_update(event: stripe.Event):
    try:
        invoice: stripe.Invoice = event.data.object
        subscription = UserMembership.objects.get(
            external_subscription_id=invoice.subscription
        )
        Payment.objects.update_or_create(
            external_payment_id=invoice.payment_intent,
            defaults={
                "user_membership": subscription,
                "subtotal": invoice.subtotal if invoice.subtotal else 0,
                "tax": invoice.tax if invoice.tax is not None else 0,
                "total": invoice.total if invoice.total else 0,
                "status": invoice.status,
            },
        )
    except Exception as err:
        logger.error(f"Creating Payment from webhook: {err}")
        raise


def handle_payment_creation(event: stripe.Event):
    try:
        data: stripe.PaymentIntent = event.data.object
        Payment.objects.update_or_create(
            external_payment_id=data.id,
            defaults={
                "status": data.status,
                "description": data.description,
                "payment_method": PaymentMethod.objects.get(
                    external_payment_method_id=data.payment_method
                ),
            },
        )
    except Exception as err:
        logger.error(f"Updating Payment from webhook: {err}")
        raise


def payment_method_update_or_create(stripe_payment_intent: stripe.PaymentMethod):
    customer = CustomerUser.objects.get(
        external_customer_id=stripe_payment_intent.customer
    )

    payment_method_id = stripe_payment_intent["payment_method"]
    stripe_payment_method = stripe.PaymentMethod.retrieve(payment_method_id)

    billing_details = stripe_payment_method.billing_details
    card_details = stripe_payment_method.card

    PaymentMethod.objects.update_or_create(
        external_payment_method_id=stripe_payment_method.id,
        defaults={
            "external_payment_method_id": stripe_payment_method.id,
            "user": customer,
            "card_name": billing_details.name or "",
            "type": getattr(card_details, "brand", None),
            "last_four": getattr(card_details, "last4", None),
            "expiration_month": getattr(card_details, "exp_month", None),
            "expiration_year": getattr(card_details, "exp_year", None),
        },
    )


def handle_payment_method_creation(event: stripe.Event):
    try:
        data = event.data.object
        payment_method_update_or_create(data)
    except Exception as err:
        logger.error(f"Creating PaymentMethod from webhook: {err}")
        raise
