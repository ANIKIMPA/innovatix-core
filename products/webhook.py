import logging

from innovatix.users.models import CustomerUser
from products.models import Membership, UserMembership
from products.utils import create_user_membership

logger = logging.getLogger("django")


def subscription_update_or_create(stripe_subscription, **kwargs):
    UserMembership.objects.update_or_create(
        external_subscription_id=stripe_subscription.id,
        defaults={
            "user": CustomerUser.objects.get(
                external_customer_id=stripe_subscription.customer
            ),
            "membership": Membership.objects.get(
                external_product_id=stripe_subscription.plan.product
            ),
            "recurring_price": stripe_subscription.plan.amount,
            "recurring_payment": stripe_subscription.plan.interval,
            "external_subscription_id": stripe_subscription.id,
            "status": stripe_subscription.status,
            **kwargs,
        },
    )


def handle_subscription_creation(event):
    try:
        data = event.data.object
        subscription_update_or_create(data)
    except Exception as err:
        logger.error(f"Creating UserMembership from webhook: {err}")


def handle_subscription_update(event):
    try:
        data = event.data.object
        subscription_update_or_create(data)
    except Exception as err:
        logger.error(f"Updating Subscription from webhook: {err}")


def handle_product_deleted(event):
    try:
        data = event.data.object
        Membership.objects.filter(external_product_id=data.id).delete()
    except Exception as err:
        logger.error(f"Failed deleting Product from webhook: {err}")
