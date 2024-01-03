from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from innovatix.users.models import CustomerUser


class CoreAbstractPaymentGateway:
    """
    Abstract class that defines a blueprint for payment gateways.
    """

    def create_customer(self, data: dict):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )

    def update_customer(self, obj: CustomerUser):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )

    def delete_customer(self, customer_id: str):
        raise NotImplementedError(
            "This method should be implemented in a specific payment gateway subclass"
        )
