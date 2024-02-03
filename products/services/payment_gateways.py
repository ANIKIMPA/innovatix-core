import json
import logging
import math
from typing import Any

from django.http import HttpResponse
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from innovatix.core.services.payment_gateways import CoreStripePaymentGateway
from products.constants import INITIAL_PAYMENT_PRODUCT_NAME
from products.models import Membership, UserMembership

logger = logging.getLogger("django")


class StripePaymentGateway(CoreStripePaymentGateway):
    """
    Stripe-specific implementation of the Stripe payment gateway.
    """

    TRANSACTION_FEE_PERCENT = 0.029
    TRANSACTION_FEE_CENTS = 30

    def entry_cost_product_id(self) -> str:
        try:
            return Membership.objects.get(
                name=INITIAL_PAYMENT_PRODUCT_NAME
            ).external_product_id
        except Membership.DoesNotExist:
            return ""

    def calculate_cost_with_fee(self, price: float) -> float:
        """
        Calculate the cost with the transaction fee.
        """
        if price == 0:
            return 0

        cost = price + self.TRANSACTION_FEE_CENTS
        cost = cost / (1 - self.TRANSACTION_FEE_PERCENT)

        return math.ceil(cost)

    def calculate_service_fee(self, price: float) -> float:
        """
        Calculate the transaction fee for a given price.
        """
        if price == 0:
            return 0

        return math.ceil(
            self.calculate_cost_with_fee(price) * self.TRANSACTION_FEE_PERCENT
            + self.TRANSACTION_FEE_CENTS
        )

    def create_checkout_session(self, line_items, metadata, success_url, cancel_url):
        """
        Create a Stripe payment session.

        :param line_items: List of items for the payment session.
        :param metadata: Additional data for the payment session.
        :param success_url: URL to redirect to upon successful payment.
        :param cancel_url: URL to redirect to if payment is canceled.
        :return: URL of the Stripe payment session or None if session creation fails.
        """

        try:
            checkout_session = self.stripe.checkout.Session.create(
                line_items=line_items,
                metadata=metadata,
                phone_number_collection={
                    "enabled": True,
                },
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return checkout_session
        except Exception as e:
            logger.error(f"Failed creating Stripe checkout session: {e}")
            return HttpResponse(status=500)

    def create_confirm_subscription(
        self,
        customer_id: str,
        payment_method_id: str,
        membership: Membership,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Creates and confirms a subscription for a customer, including a one-time charge.

        This method creates a subscription for the specified customer and items, and confirms
        the associated PaymentIntent with the specified payment method. Additionally, it creates
        an InvoiceItem for a one-time charge, such as a setup fee or joining fee, which is added
        to the first invoice for the subscription.

        :param customer_id: The ID of the customer in Stripe.
        :param one_time_price_id: The ID of the price for the one-time charge in Stripe.
        :param recurring_price_id: The ID of the price for the recurring charge in Stripe.
        :param payment_method_id: The ID of the payment method to use for the subscription.
        :param kwargs: Additional parameters, such as IP address and user agent.
        :return: The status and client secret of the PaymentIntent.
        """

        try:
            self.stripe.InvoiceItem.create(
                customer=customer_id,
                description="One-time setup fee",
                price_data={
                    "product": self.entry_cost_product_id(),
                    "unit_amount": self.calculate_cost_with_fee(membership.entry_cost),
                    "currency": "usd",
                },
            )

            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {
                        "price_data": {
                            "product": membership.external_product_id,
                            "unit_amount": self.calculate_cost_with_fee(
                                membership.recurring_price
                            ),
                            "currency": "usd",
                            "recurring": {
                                "interval": membership.recurring_payment,
                            },
                        }
                    },
                ],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )

            # Confirm intent with collected payment method
            payment_intent = self.stripe.PaymentIntent.confirm(
                subscription.latest_invoice.payment_intent.id,
                payment_method=payment_method_id,
                mandate_data={
                    "customer_acceptance": {
                        "type": "online",
                        "online": {
                            "ip_address": kwargs.get("ip_address"),
                            "user_agent": kwargs.get("user_agent"),
                        },
                    },
                },
            )

            return {
                "status": 200,
                "client_secret": payment_intent.client_secret,
                "message": "Payment succeeded",
                "code": payment_intent.status,
                "error": {
                    "message": "There was an error processing your payment. Try again later."
                },
            }

        except self.stripe.error.CardError as err:
            return {
                "status": err.http_status,
                "client_secret": None,
                "message": err.user_message,
                "code": err.code,
                "error": {"message": err.user_message},
            }

        except self.stripe.error.InvalidRequestError as err:
            raise Exception(f"Invalid Request: {err.user_message}")

        except Exception as err:
            logger.error(f"Failed creating Stripe subscription: {err}")
            return {
                "status": err.http_status,
                "client_secret": None,
                "message": err.user_message,
                "code": err.code,
                "error": {
                    "message": _(
                        "There was an error processing your payment. Try again later."
                    )
                },
            }

    def create_initial_payment_product(self, description: str):
        try:
            product = self.stripe.Product.create(
                name=INITIAL_PAYMENT_PRODUCT_NAME,
                description=description,
            )

            return product
        except Exception as err:
            logger.error(f"Failed creating Stripe entry product: {err}")
            raise Exception(_(f"Failed creating Stripe entry product: {err}"))

    def create_membership(self, membership: Membership):
        try:
            product = self.stripe.Product.create(
                name=membership.name,
                description=(
                    strip_tags(membership.short_description)
                    if membership.short_description
                    else None
                ),
                metadata={"type": "membership"},
            )

            return product
        except Exception as err:
            logger.error(f"Failed creating Stripe membership: {err}")
            raise Exception(_(f"Failed creating Stripe membership: {err}"))

    def update_membership(self, membership: Membership):
        try:
            return self.stripe.Product.modify(
                membership.external_product_id,
                name=membership.name,
                description=strip_tags(membership.short_description),
                metadata={"type": "membership"},
            )
        except self.stripe.error.InvalidRequestError as err:
            if err.user_message.startswith("No such product"):
                return self.create_membership(membership)

            logger.error(f"Failed updating Stripe membership: {err}")
            raise Exception(f"Failed updating Stripe membership: {err}")

    def delete_membership(self, membership: Membership):
        try:
            self.stripe.Product.delete(membership.external_product_id)
        except Exception as err:
            logger.error(f"Failed to delete membership from Stripe: {str(err)}")
            raise Exception(f"Failed to delete membership from Stripe: {str(err)}")

    def update_subscription(self, subscription: UserMembership):
        try:
            return self.stripe.Subscription.modify(
                subscription.external_subscription_id,
                cancel_at_period_end=False,
                proration_behavior="none",
                items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product": subscription.membership.external_product_id,
                            "unit_amount": subscription.recurring_price,
                            "recurring": {"interval": subscription.recurring_payment},
                        }
                    },
                ],
            )
        except Exception as err:
            logger.error(f"Failed to updating subscription from Stripe: {str(err)}")
            return None

    def construct_event(self, payload: dict) -> dict:
        try:
            event = self.stripe.Event.construct_from(
                json.loads(payload), self.stripe.api_key
            )
            return event
        except Exception as err:
            logger.error(f"Failed to construct event from Stripe: {str(err)}")
            raise
