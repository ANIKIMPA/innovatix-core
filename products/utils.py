from typing import Any

from products.models import Membership, UserMembership
from users.models import CustomerUser


def create_membership(**kwargs: Any) -> Membership:
    model_params = {
        "is_visible": True,
    }
    model_params.update(**kwargs)

    return Membership.objects.create(**model_params)


def create_user_membership(
    user: CustomerUser, membership: Membership, **kwargs: Any
) -> UserMembership:
    model_params = {"user": user, "membership": membership, "status": "active"}
    model_params.update(**kwargs)

    return UserMembership.objects.create(**model_params)


# Fake data
def create_fake_membership(**kwargs: Any) -> Membership:
    model_params = {
        "external_product_id": "prod_membership1",
        "name": "Test Membership",
        "slug": "test-membership",
        "entry_cost": 500,
        "recurring_price": 1049,
        "recurring_payment": "month",
    }
    model_params.update(**kwargs)
    return create_membership(**model_params)


def create_fake_subscription(
    user: CustomerUser, membership: Membership, **kwargs: Any
) -> UserMembership:
    model_params = {
        "user": user,
        "membership": membership,
        "external_subscription_id": "sub_1NvXdlKUAEHamOC3f2qyO7U9",
        "recurring_price": membership.recurring_price,
        "recurring_payment": membership.recurring_payment,
    }
    model_params.update(**kwargs)
    return create_user_membership(**model_params)
