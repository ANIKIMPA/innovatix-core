import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from products.services.payment_gateways import StripePaymentGateway


class Command(BaseCommand):
    help = "Copy Stripe live data to test environment"

    def handle(self, *args, **options):
        # Setup Stripe with the live API key
        payment_gateway = StripePaymentGateway(os.environ.get("STRIPE_SECRET_KEY_LIVE"))
        customers = payment_gateway.stripe.Customer.list(limit=20).data

        # Fetch all payment methods and payments for each customer
        for customer in customers:
            customer_id = customer["id"]

            # Fetch charges (payments)
            customer["payments"] = payment_gateway.stripe.Charge.list(
                customer=customer.id, limit=1
            ).data

        # Setup Stripe with the test API key
        payment_gateway = StripePaymentGateway(settings.STRIPE_SECRET_KEY)

        for customer in customers:
            payments = customer["payments"]

            # Check if last payment was susccessful
            if payments and payments[0]["status"] == "succeeded":
                test_payment_method = "pm_card_us"
            else:
                # This card will be declined
                test_payment_method = "pm_card_visa_chargeDeclinedInsufficientFunds"

            try:
                # Create a Customer and attach the PaymentMethod
                test_customer = payment_gateway.stripe.Customer.create(
                    payment_method=test_payment_method,
                    email=customer["email"],
                    name=customer["name"],
                    phone=customer["phone"],
                    description=customer["description"],
                    invoice_settings={
                        "default_payment_method": test_payment_method,
                    },
                )
            except payment_gateway.stripe.error.StripeError as e:
                test_customer = payment_gateway.stripe.Customer.create(
                    email=customer["email"],
                    name=customer["name"],
                    phone=customer["phone"],
                    description=customer["description"],
                )
                print(f"Could not set the default payment method: {e}")

            for payment in payments:
                created_date = datetime.utcfromtimestamp(payment["created"])
                created_date_str = created_date.strftime("%Y-%m-%d")

                try:
                    payment_gateway.stripe.PaymentIntent.create(
                        amount=payment["amount"],
                        currency=payment["currency"],
                        customer=test_customer["id"],
                        payment_method=test_payment_method,
                        confirm=True,
                        metadata={
                            "created_date": created_date_str,
                            "original_status": payment["status"],
                        },
                    )
                except payment_gateway.stripe.error.StripeError as e:
                    print(f"Failded creating Stripe payment: {e}")
