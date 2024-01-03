import logging
from typing import Any

from innovatix.geo_territories.models import Country, Province
from innovatix.users.constants import DEFAULT_COUNTRY_CODE, DEFAULT_PROVINCE_CODE

logger = logging.getLogger("django")


def create_country(**kwargs: dict[str, Any]) -> Country:
    model_params = {}
    model_params.update(**kwargs)

    return Country.objects.create(**model_params)


def create_province(country: Country, **kwargs: dict[str, Any]) -> Province:
    model_params = {"country": country}
    model_params.update(**kwargs)

    return Province.objects.create(**model_params)


def get_default_country() -> Country:
    try:
        return Country.objects.get(code=DEFAULT_COUNTRY_CODE)
    except Country.DoesNotExist as err:
        logger.error(f"Fetching the default country from the DB: {err}")
        raise Country.DoesNotExist


def get_default_province() -> Province:
    try:
        return Province.objects.get(
            code=DEFAULT_PROVINCE_CODE, country=get_default_country()
        )
    except Province.DoesNotExist as err:
        logger.error(f"Fetching the default country from the DB: {err}")
        raise Province.DoesNotExist
