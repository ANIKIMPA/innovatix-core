import logging

from innovatix.core.utils import log_change, log_creation, log_deletion
from innovatix.geo_territories.models import Country, Province
from innovatix.users.models import CustomerUser
from innovatix.users.utils import create_customer_user, is_an_existing_customer

logger = logging.getLogger("django")


def get_sanitized_data(stripe_customer):
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


def handle_customer_creation(event):
    try:
        data = event.data.object

        if not data.email or is_an_existing_customer(data.email):
            # Reject customer creation with an existent email.
            return

        # Create CustomerUser with sanitized data
        customer = create_customer_user(**get_sanitized_data(data))
        log_creation(
            customer, message=f'Added from {getattr(data.metadata, "from", "Stripe")}'
        )
    except Exception as err:
        logger.error(f"Failed creating CustomerUser from webhook: {err}")


def handle_customer_update(event):
    try:
        data = event.data.object

        if not CustomerUser.objects.filter(external_customer_id=data.id).exists():
            return handle_customer_creation(event)

        # Update CustomerUser with sanitized data
        customer = CustomerUser.objects.filter(external_customer_id=data.id).update(
            **get_sanitized_data(data)
        )

        log_change(
            customer,
            message=f'Changed from {getattr(data.metadata, "from", "Stripe")}',
        )
    except Exception as err:
        logger.error(f"Failed updating CustomerUser from webhook: {err}")


def handle_cusomer_deletion(event):
    try:
        data = event.data.object

        customer = CustomerUser.objects.filter(external_customer_id=data.id).first()

        if customer:
            log_deletion(customer)
            customer.delete()
    except Exception as err:
        logger.error(f"Failed deleting CustomerUser from webhook: {err}")
