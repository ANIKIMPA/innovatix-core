from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from products.models import Membership


class AbstractPaymentGateway:
    """
    Abstract class that defines a blueprint for payment gateways.
    """

    def create_checkout_session(self, line_items, metadata, success_url, cancel_url):
        """
        Create a payment session.

        :param line_items: List of items for the payment session.
        :param metadata: Additional data for the payment session.
        :param success_url: URL to redirect to upon successful payment.
        :param cancel_url: URL to redirect to if payment is canceled.
        :return: URL of the payment session or None if session creation fails.
        """
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )

    def create_customer(self, data: dict):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )

    def create_confirm_subscription(
        self,
        **kwargs,
    ):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )

    def create_membership(self, membership: Membership):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )

    def update_membership(self, membership: Membership):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )

    def delete_membership(self, membership: Membership):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )
