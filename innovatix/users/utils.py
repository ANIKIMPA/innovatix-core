from __future__ import annotations

from typing import TYPE_CHECKING, Any

from innovatix.users.models import CoreContactModel, CustomerUser

if TYPE_CHECKING:
    from innovatix.geo_territories.models import Country, Province


def create_customer_user(
    province: Province, country: Country, **kwargs: Any
) -> CustomerUser:
    model_params = {
        "province": province,
        "country": country,
    }
    model_params.update(**kwargs)

    return CustomerUser.objects.create_user(**model_params)


def create_contact(**kwargs: Any) -> CoreContactModel:
    return CoreContactModel.objects.create(**kwargs)


# Fake data
def create_fake_customer_user(
    province: Province, country: Country, **kwargs: Any
) -> CustomerUser:
    model_params = {
        "province": province,
        "country": country,
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "thepassword",
        "phone_number": "+16502532222",
        "address1": "Test Address",
        "city": "Test City",
        "zip": "00000",
    }
    model_params.update(**kwargs)

    return create_customer_user(**model_params)


def create_fake_contact(**kwargs: Any) -> CoreContactModel:
    model_params = {
        "name": "Test",
        "email": "test@example.com",
        "phone_number": "9393316860",
        "message": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Expedita ipsum illum odio ea velit nulla veniam maiores voluptatum eveniet impedit dolor incidunt id possimus autem quos ullam, dolorem quisquam delectus?",
    }
    model_params.update(**kwargs)

    return create_contact(**model_params)


def get_user_info_fake_session_data(country, province, **kwargs):
    data = {
        "email": "user.test@example.com",
        "phone_number": "7872594465",
        "first_name": "John",
        "last_name": "Doe",
        "country": country.pk,
        "province": province.pk,
        "address1": "Test street",
        "address2": "",
        "city": "Testland",
        "company": "",
        "zip": "00956",
        "accept_terms_condition": True,
    }
    data.update(**kwargs)
    return data


def is_an_existing_customer(email: str) -> bool:
    return CustomerUser.objects.filter(email=email).exists()