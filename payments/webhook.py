import logging

import stripe

from innovatix.users.models import CustomerUser
from payments.models import Payment, PaymentMethod
from products.models import UserMembership

logger = logging.getLogger("django")


def handle_payment_creation(event: stripe.Event):
    try:
        data: stripe.Invoice = event.data.object
        subscription = UserMembership.objects.get(
            external_subscription_id=data.subscription
        )
        Payment.objects.create(
            external_payment_id=data.payment_intent,
            description=data.description,
            user_membership=subscription,
            subtotal=data.subtotal if data.subtotal else 0.00,
            tax=data.tax if data.tax is not None else 0.00,
            total=data.total if data.total else 0.00,
            status=data.status,
        )
    except Exception as err:
        logger.error(f"Creating Payment from webhook: {err}")
        raise


def handle_payment_update(event: stripe.Event):
    try:
        data: stripe.PaymentIntent = event.data.object
        payment = Payment.objects.get(external_payment_id=data.id)
        payment.status = data.status
        payment.description = data.description
        payment.payment_method = PaymentMethod.objects.get(
            external_payment_method_id=data.payment_method
        )
        payment.save()
    except Exception as err:
        logger.error(f"Updating Payment from webhook: {err}")
        raise


def payment_method_update_or_create(stripe_payment_method: stripe.PaymentMethod):
    customer = CustomerUser.objects.get(
        external_customer_id=stripe_payment_method.customer
    )

    PaymentMethod.objects.update_or_create(
        external_payment_method_id=stripe_payment_method.id,
        defaults={
            "external_payment_method_id": stripe_payment_method.id,
            "user": customer,
            "card_name": stripe_payment_method.billing_details.name or "",
            "type": getattr(stripe_payment_method.card, "brand", None),
            "last_four": getattr(stripe_payment_method.card, "last4", None),
            "expiration_month": getattr(stripe_payment_method.card, "exp_month", None),
            "expiration_year": getattr(stripe_payment_method.card, "exp_year", None),
        },
    )


def handle_payment_method_creation(event: stripe.Event):
    try:
        data = event.data.object
        payment_method_update_or_create(data)
    except Exception as err:
        logger.error(f"Creating PaymentMethod from webhook: {err}")
        raise
