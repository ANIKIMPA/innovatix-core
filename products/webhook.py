import logging
from typing import Any

import stripe

from innovatix.users.models import CustomerUser
from products.models import Membership, UserMembership

logger = logging.getLogger("django")


def handle_update_or_create(
    stripe_subscription: stripe.Subscription, **kwargs: dict[str, Any]
) -> tuple[UserMembership, bool]:
    plan = stripe_subscription.get("plan") or {}
    return UserMembership.objects.update_or_create(
        external_subscription_id=stripe_subscription.id,
        defaults={
            "user": CustomerUser.objects.get(
                external_customer_id=stripe_subscription.customer
            ),
            "membership": Membership.objects.get(
                external_product_id=plan.get("product")
            ),
            "recurring_price": plan.get("amount"),
            "recurring_payment": plan.get("interval"),
            "external_subscription_id": stripe_subscription.id,
            "status": stripe_subscription.status,
            **kwargs,
        },
    )


def handle_creation(event: stripe.Event) -> UserMembership:
    try:
        subscription, _ = handle_update_or_create(event.data.object)

        return subscription
    except Exception as err:
        logger.error(f"Creating Subscription from webhook: {err}")
        raise


def handle_update(event: stripe.Event):
    try:
        subscription, _ = handle_update_or_create(event.data.object)

        return subscription
    except Exception as err:
        logger.error(f"Updating Subscription from webhook: {err}")
        raise


def handle_product_deleted(event: stripe.Event):
    try:
        data: stripe.Product = event.data.object
        Membership.objects.filter(external_product_id=data.id).delete()
    except Exception as err:
        logger.error(f"Failed deleting Product from webhook: {err}")
        raise
