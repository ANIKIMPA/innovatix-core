from datetime import datetime
from typing import Any

from payments.models import Payment, PaymentMethod
from products.models import UserMembership
from users.models import CustomerUser


def create_payment_method(user: CustomerUser, **kwargs: Any) -> PaymentMethod:
    model_params = {
        "user": user,
    }
    model_params.update(**kwargs)

    return PaymentMethod.objects.create(**model_params)


def create_payment(
    user_membership: UserMembership, payment_method: PaymentMethod, **kwargs: Any
) -> Payment:
    model_params = {
        "user_membership": user_membership,
        "payment_method": payment_method,
    }
    model_params.update(**kwargs)

    return Payment.objects.create(**model_params)


# Fake data
def create_fake_payment_method(user: CustomerUser, **kwargs: Any) -> PaymentMethod:
    current_year = datetime.now().year
    model_params = {
        "card_name": "4242 4242 4242 4242",
        "type": "visa",
        "last_four": "1234",
        "expiration_month": "08",
        "expiration_year": str(
            current_year + 2,
        ),
    }
    model_params.update(**kwargs)

    return create_payment_method(user, **model_params)


def create_fake_payment(
    user_membership: UserMembership, payment_method: PaymentMethod, **kwargs: Any
) -> Payment:
    model_params = {
        "user_membership": user_membership,
        "payment_method": payment_method,
        "subtotal": 10.00,
        "tax": 0.00,
        "total": 10.00,
        "status": "completed",
    }
    model_params.update(**kwargs)

    return create_payment(**model_params)
