from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from core.services import payment_gateway
from products.models import Membership


class Command(BaseCommand):
    help = "Create a subscription for all Stripe customers who don't have a subscription yet"

    def handle(self, *args, **options):
        seen_emails = []
        repeated_emails = {}
        existing_subscriber_emails = []
        no_payment_emails = []
        created_subscription_emails = []
        created_subscription_emails_to_start_tomorrow = []

        customers = payment_gateway.fetch_all("Customer", limit=100)

        for customer in customers:
            if customer["email"] in seen_emails:
                repeated_emails.update(
                    {customer["email"]: repeated_emails.get(customer["email"], 1) + 1}
                )
                continue

            if (
                customer["subscriptions"]
                and customer["subscriptions"]["total_count"] > 0
            ):
                seen_emails += [customer["email"]]
                existing_subscriber_emails.append(customer.email)
                continue

            payments = payment_gateway.fetch_all(
                "Charge", customer=customer.id, limit=100
            )

            if not payments:
                no_payment_emails.append(customer.email)
                continue

            seen_emails += [customer["email"]]

            if payments[0].amount == 29000:
                membership = Membership.objects.get(recurring_price=29000)
            else:
                membership = Membership.objects.get(recurring_price=2495)

            if payments[0].status != "succeeded":
                self.create_subscription(membership, customer, payments, days=1)
                created_subscription_emails_to_start_tomorrow.append(customer.email)
                continue

            self.create_subscription(membership, customer, payments)
            created_subscription_emails.append(customer.email)

        print(f"Repeated emails: ({len(repeated_emails)})")
        print(repeated_emails)
        print()
        print(f"Seen emails: ({len(seen_emails)})")
        print(seen_emails)
        print()
        print(f"No payment emails: ({len(no_payment_emails)})")
        print(no_payment_emails)
        print()
        print(f"Existing subscriber emails: ({len(existing_subscriber_emails)})")
        print(existing_subscriber_emails)
        print()
        print(f"Subscription created emails: ({len(created_subscription_emails)})")
        print(created_subscription_emails)
        print()
        print(
            f"Subscription created emails for tomorrow: ({len(created_subscription_emails_to_start_tomorrow)})"
        )
        print(created_subscription_emails_to_start_tomorrow)

    def create_subscription(self, membership, customer, payments, **kwargs):
        stripe_timestamp = payments[0]["created"]
        stripe_datetime = datetime.fromtimestamp(stripe_timestamp)

        if not kwargs.get("days", None):
            kwargs = {f"{membership.recurring_payment}s": 1}

        next_billing_date = stripe_datetime + relativedelta(**kwargs)

        return payment_gateway.stripe.Subscription.create(
            customer=customer["id"],
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
            default_payment_method=customer.invoice_settings.get(
                "default_payment_method", None
            ),
            billing_cycle_anchor=next_billing_date,
            backdate_start_date=payments[-1].created,
            proration_behavior="none",
            payment_settings={"save_default_payment_method": "on_subscription"},
        )
