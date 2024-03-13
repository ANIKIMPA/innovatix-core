from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import stripe
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from innovatix.core.services.abstract_payment_gateways import CoreAbstractPaymentGateway

if TYPE_CHECKING:
    from innovatix.users.models import CustomerUser

logger = logging.getLogger("django")


class CoreStripePaymentGateway(CoreAbstractPaymentGateway):
    """
    Stripe-specific implementation of the Stripe payment gateway.
    """

    def __init__(self, api_key: str):

        self.stripe = stripe
        self.stripe.api_key = api_key

    def _get_customer_data(
        self, obj: CustomerUser, **kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "email": obj.email,
            "name": f"{obj.first_name} {obj.last_name}",
            "phone": obj.phone_number,
            "shipping": {
                "address": {
                    "city": obj.city,
                    "country": obj.country.code,
                    "line1": obj.address1,
                    "line2": obj.address2,
                    "postal_code": obj.zip,
                    "state": obj.province.code,
                },
                "name": f"{obj.first_name} {obj.last_name}",
            },
            "address": {
                "city": obj.city,
                "country": obj.country.code,
                "line1": obj.address1,
                "line2": obj.address2,
                "postal_code": obj.zip,
                "state": obj.province.code,
            },
            "payment_method": kwargs.get("payment_method_id", None),
            "metadata": {
                "first_name": obj.first_name,
                "last_name": obj.last_name,
                "from": settings.COMPANY_NAME,
            },
        }

    def create_customer(self, obj: CustomerUser, **kwargs):
        """
        Create a Stripe customer.

        :param obj: CustomerUser model instance.
        """

        return self.stripe.Customer.create(**self._get_customer_data(obj, **kwargs))

    def update_customer(self, obj: CustomerUser) -> stripe.Customer:
        """
        Update Stripe customer.

        :param obj: CustomerUser model instance.
        """

        try:
            if not obj.external_customer_id:
                return self.create_customer(obj)

            return self.stripe.Customer.modify(
                obj.external_customer_id, **self._get_customer_data(obj)
            )
        except Exception as e:
            logger.error(f"Failed updating or creating Stripe customer: {e}")
            raise

    def delete_customer(self, customer_id: str):
        try:
            return self.stripe.Customer.delete(customer_id)
        except Exception as err:
            logger.error(f"Failed deleting Stripe customer: {err}")

    def fetch_all(
        self, resource: str, all: bool = True, **kwargs: dict[str, Any]
    ) -> list[Any]:
        response = {"has_more": True}
        starting_after = None

        all_items = []

        while response.get("has_more"):
            stripe_resource = getattr(self.stripe, resource)
            response = stripe_resource.list(starting_after=starting_after, **kwargs)
            items = response["data"]
            all_items.extend(items)

            if response.get("has_more"):
                starting_after = items[-1]["id"]

            if not all:
                break

        return all_items
