import logging
from typing import Any

from innovatix.users.models import CustomerUser
from products.models import Membership, UserMembership

logger = logging.getLogger("django")


class SubscriptionStripeWebhook:
    def __init__(self, event):
        self.event = event

    def handle_update_or_create(
        self, **kwargs: dict[str, Any]
    ) -> tuple[UserMembership, bool]:
        stripe_subscription = kwargs.get("stripe_subscription", self.event.data.object)

        return UserMembership.objects.update_or_create(
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

    def handle_creation(self) -> UserMembership:
        try:
            subscription, _ = self.handle_update_or_create()

            return subscription
        except Exception as err:
            logger.error(f"Creating Subscription from webhook: {err}")
            raise

    def handle_update(self):
        try:
            subscription, _ = self.handle_update_or_create()

            return subscription
        except Exception as err:
            logger.error(f"Updating Subscription from webhook: {err}")
            raise


def handle_product_deleted(event):
    try:
        data = event.data.object
        Membership.objects.filter(external_product_id=data.id).delete()
    except Exception as err:
        logger.error(f"Failed deleting Product from webhook: {err}")
        raise
