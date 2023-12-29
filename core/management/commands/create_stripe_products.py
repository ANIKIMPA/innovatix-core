import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from core.services import payment_gateway
from products.models import Membership


class Command(BaseCommand):
    help = "Copy Stripe live data to test environment"

    def handle(self, *args, **options):
        # Setup Stripe with the live API key
        product = payment_gateway.create_initial_payment_product()

        print(f'ENTRY_COST_PRODUCT_ID = "{product.id}"')
        print("------")
        print(
            f"Please replace the ENTRY_COST_PRODUCT_ID constant located in 'core/services/payment_gateways.py' with this id:\n{product.id}"
        )

        memberships = Membership.objects.all()

        for membership in memberships:
            product = payment_gateway.update_membership(membership)
            membership.external_product_id = product.id
            membership.save()
