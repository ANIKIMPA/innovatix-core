import phonenumbers
from django.core.exceptions import ValidationError

from innovatix.geo_territories.constants import DEFAULT_COUNTRY_CODE


class PhoneNumberService:
    @staticmethod
    def parse_phone_number(
        phone_number: str, country_code: str = DEFAULT_COUNTRY_CODE
    ) -> phonenumbers.phonenumber.PhoneNumber:
        return phonenumbers.parse(phone_number, country_code)

    @staticmethod
    def format_phone_number(
        phone_number: str, country_code: str = DEFAULT_COUNTRY_CODE
    ) -> str:
        parsed_phone = PhoneNumberService.parse_phone_number(phone_number, country_code)
        return phonenumbers.format_number(
            parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

    @staticmethod
    def validate_phone_number(
        phone_number: str, country_code: str = DEFAULT_COUNTRY_CODE
    ):
        parsed_number = None

        try:
            parsed_number = PhoneNumberService.parse_phone_number(
                phone_number, country_code
            )
        except phonenumbers.phonenumberutil.NumberParseException as err:
            raise ValidationError([str(err)])

        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(["The phone number entered is not valid."])
