from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from innovatix.users.models import CustomerUser
from innovatix.users.models.customer_user import CustomerUser
from innovatix.users.webhook import get_sanitized_data
from payments.models import Payment, PaymentMethod
from payments.webhook import payment_method_update_or_create
from products.models import UserMembership
from products.services import payment_gateway
from products.webhook import subscription_update_or_create


class Command(BaseCommand):
    help = "Sync local database with Stripe data"

    def __init__(self):
        super().__init__()

        self.customer_ids = []

    def handle(self, *args, **kwargs):
        self.sync_customers()
        self.sync_payment_methods()
        self.sync_subscriptions()
        self.sync_payments()
        self.sync_invoices()

    def sync_customers(self):
        CustomerUser.objects.all().delete()

        stripe_customers = payment_gateway.fetch_all("Customer", limit=100)

        for stripe_customer in stripe_customers:
            CustomerUser.objects.update_or_create(
                email=stripe_customer.email,
                defaults=get_sanitized_data(stripe_customer),
            )

            self.customer_ids.append(stripe_customer.id)

    def sync_subscriptions(self):
        stripe_subscriptions = payment_gateway.fetch_all("Subscription", limit=100)
        for stripe_subscription in stripe_subscriptions:
            # Convert timestamp to a datetime object
            dt_object = datetime.fromtimestamp(stripe_subscription.created)
            aware_dt_object = timezone.make_aware(dt_object)

            subscription_update_or_create(
                stripe_subscription, date_subscribed=aware_dt_object
            )

    def sync_payment_methods(self):
        for stripe_customer_id in self.customer_ids:
            stripe_payment_methods = payment_gateway.fetch_all(
                "PaymentMethod", customer=stripe_customer_id, limit=100
            )
            for stripe_payment_method in stripe_payment_methods:
                payment_method_update_or_create(stripe_payment_method)

    def sync_payments(self):
        Payment.objects.all().delete()

        stripe_payments = payment_gateway.fetch_all("PaymentIntent", limit=100)
        for stripe_payment in stripe_payments:
            dt_object = datetime.fromtimestamp(stripe_payment.created)
            aware_dt_object = timezone.make_aware(dt_object)
            payment_method = PaymentMethod.objects.filter(
                external_payment_method_id=stripe_payment.payment_method
            ).first()
            Payment.objects.update_or_create(
                external_payment_id=stripe_payment.id,
                defaults={
                    "external_payment_id": stripe_payment.id,
                    "description": stripe_payment.description,
                    "user_membership": None,
                    "payment_method": payment_method,
                    "subtotal": stripe_payment.amount,
                    "tax": 0,
                    "total": stripe_payment.amount,
                    "status": stripe_payment.status,
                    "date": aware_dt_object,
                },
            )

    def sync_invoices(self):
        stripe_invoices = payment_gateway.fetch_all("Invoice", limit=100)

        for stripe_invoice in stripe_invoices:
            payment = Payment.objects.get(
                external_payment_id=stripe_invoice.payment_intent
            )

            payment.user_membership = UserMembership.objects.filter(
                external_subscription_id=stripe_invoice.subscription
            ).first()
            payment.subtotal = stripe_invoice.subtotal or 0
            payment.tax = stripe_invoice.tax or 0
            payment.total = stripe_invoice.total or 0
            payment.save()
