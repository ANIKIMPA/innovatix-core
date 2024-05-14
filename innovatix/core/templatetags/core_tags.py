from django import template
from innovatix.core.services.phone_number_service import PhoneNumberService
from innovatix.users.constants import DEFAULT_COUNTRY_CODE

register = template.Library()


@register.filter
def cents_to_dollars(value: float) -> float:
    return value / 100


@register.filter
def dollar_format(value: float) -> str:
    try:
        return "${:,.2f}".format(value)
    except ValueError:
        return str(value)


@register.simple_tag(takes_context=True)
def mark_if_active_link(context, active_page):
    """
    Checks if the given active_page matches the 'url_name' in the context.
    If it does, returns 'active', otherwise returns an empty string.
    This can be used to add the 'active' CSS class to the active page in the navigation menu.
    """
    if "url_name" in context:
        if context["url_name"] == active_page:
            return "active"

    return ""


@register.filter
def to_dict(instance):
    return instance.__dict__


@register.filter
def dir(instance):
    return dir(instance)


@register.filter
def contents(field):
    field_name = field.field.get("name")

    if field_name in field.form.fields:
        return field.form[field_name].initial

    return field.contents()


@register.filter
def help_text(field):
    field_name = field.field.get("name")
    return field.form[field_name].help_text


@register.filter(name="phone_format")
def phone_format(value: str):
    try:
        return PhoneNumberService.format_phone_number(value, DEFAULT_COUNTRY_CODE)
    except Exception:
        return value
