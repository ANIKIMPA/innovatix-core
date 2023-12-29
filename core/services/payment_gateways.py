from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from core.services.abstract_payment_gateways import AbstractPaymentGateway
from users.models import CustomerUser

if TYPE_CHECKING:
    from products.models import Membership, UserMembership

logger = logging.getLogger("django")


class StripePaymentGateway(AbstractPaymentGateway):
    """
    Stripe-specific implementation of the payment gateway.
    """

    ENTRY_COST_PRODUCT_ID = "prod_OskLdFybEvC2jP"

    def __init__(self, api_key):
        import stripe

        self.stripe = stripe
        self.stripe.api_key = api_key

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

    def _get_customer_data(self, obj: CustomerUser, **kwargs):
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
            "source": kwargs.get("payment_method_id", None),
            "metadata": {
                "first_name": obj.first_name,
                "last_name": obj.last_name,
                "company": obj.company,
                "from": "PR Gun",
            },
        }

    def create_customer(self, obj: CustomerUser, **kwargs):
        """
        Create a Stripe customer.

        :param obj: CustomerUser model instance.
        """

        return self.stripe.Customer.create(**self._get_customer_data(obj, **kwargs))

    def update_customer(self, obj: CustomerUser):
        """
        Update Stripe customer.

        :param obj: CustomerUser model instance.
        """

        try:
            return self.stripe.Customer.modify(
                obj.external_customer_id, **self._get_customer_data(obj)
            )
        except Exception as e:
            logger.error(f"Failed updating Stripe customer: {e}")
            return HttpResponse(status=500)

    def delete_customer(self, customer_id):
        try:
            return self.stripe.Customer.delete(customer_id)
        except Exception as err:
            logger.error("Failed deleting Stripe customer: {}")

    def create_confirm_subscription(
        self,
        customer_id: str,
        payment_method_id: str,
        membership: Membership,
        **kwargs,
    ):
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
                    "product": self.ENTRY_COST_PRODUCT_ID,
                    "unit_amount": membership.entry_cost,
                    "currency": "usd",
                },
            )

            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {
                        "price_data": {
                            "product": membership.external_product_id,
                            "unit_amount": membership.recurring_price,
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

    def create_initial_payment_product(self):
        try:
            product = self.stripe.Product.create(
                name="Pago por Ingreso",
                description="Pago por Ingreso como socio de la Puerto Rico Gun Law Association",
            )

            return product
        except Exception as err:
            logger.error(f"Failed creating Stripe entry product: {err}")
            raise Exception(_(f"Failed creating Stripe entry product: {err}"))

    def fetch_all(self, resource: str, all=True, **kwargs) -> list:
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

    def create_membership(self, membership: Membership):
        try:
            product = self.stripe.Product.create(
                name=membership.name,
                description=strip_tags(membership.short_description)
                if membership.short_description
                else None,
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
