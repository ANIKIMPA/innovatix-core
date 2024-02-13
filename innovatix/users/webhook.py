import logging
from typing import Any

import stripe
from innovatix.core.utils import log_change, log_creation, log_deletion
from innovatix.geo_territories.models import Country, Province
from innovatix.users.models import CustomerUser
from innovatix.users.utils import create_or_update_customer_user

logger = logging.getLogger("django")


def get_sanitized_data(
    stripe_customer: stripe.Customer,
) -> dict[str, Province | Country | str | Any | None]:
    address = stripe_customer.address or {}
    country = Country.objects.get(
        code=getattr(stripe_customer.address, "country", "US")
    )
    state = Province.objects.get(
        code=getattr(stripe_customer.address, "state", "PR"), country=country
    )

    try:
        first_name = getattr(
            stripe_customer.metadata, "first_name", stripe_customer.name.split()[0]
        )
    except Exception:
        first_name = ""

    try:
        last_name = getattr(
            stripe_customer.metadata,
            "last_name",
            " ".join(stripe_customer.name.split()[1:]),
        )
    except Exception:
        last_name = ""

    return {
        "province": state,
        "country": country,
        "email": stripe_customer.email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": stripe_customer.phone or "",
        "address1": getattr(address, "line1", ""),
        "address2": getattr(address, "line2", ""),
        "city": getattr(address, "city", ""),
        "zip": getattr(address, "postal_code", ""),
        "external_customer_id": stripe_customer.id,
    }


def handle_customer_update_or_creation(event: stripe.Event):
    try:
        data: stripe.Customer = event.data.object

        if not data.email:
            return

        sanitized_data = get_sanitized_data(data)

        # Create CustomerUser with sanitized data
        customer, created = create_or_update_customer_user(**sanitized_data)

        if created:
            log_creation(
                customer,
                message=f'Added from {getattr(data.metadata, "from", "Stripe")}',
            )
        else:
            log_change(
                customer,
                message=f'Changed from {getattr(data.metadata, "from", "Stripe")}',
            )
    except Exception as err:
        logger.error(f"Failed creating or updating CustomerUser from webhook: {err}")
        raise


def handle_customer_deletion(event: stripe.Event):
    try:
        data = event.data.object

        customer = CustomerUser.objects.filter(external_customer_id=data.id).first()

        if customer:
            log_deletion(customer)
            customer.delete()
    except Exception as err:
        logger.error(f"Failed deleting CustomerUser from webhook: {err}")
        raise
