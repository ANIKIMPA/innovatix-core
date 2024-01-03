from django import template

register = template.Library()


@register.filter
def cents_to_dollars(value):
    return value / 100


@register.filter
def dollar_format(value):
    try:
        return "${:,.2f}".format(value)
    except ValueError:
        return value


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
