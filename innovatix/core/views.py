from django.conf import settings
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView


class URLNameContextMixin:
    """
    Mixin to add the URL name to the context.

    This mixin is used to get the URL name of the current page and add it to the
    context under the key 'url_name'. This value can then be used in templates to
    determine which navigation link should be highlighted.

    For example, in your template, you can use this to conditionally apply an
    'active' class to the corresponding navigation item:

        <a href="{% url 'home' %}" class="{% if url_name == 'home' %}active{% endif %}">Home</a>
        <a href="{% url 'about' %}" class="{% if url_name == 'about' %}active{% endif %}">About</a>

    This way, the user can visually see on which page they are currently located.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context.update(
            {
                "url_name": self.request.resolver_match.url_name,
                "company_name": settings.COMPANY_NAME,
                "company_phone": settings.COMPANY_PHONE,
                "company_email": settings.EMAIL_HOST_USER,
            }
        )  # type: ignore
        return context


class CoreTemplateView(URLNameContextMixin, TemplateView):
    pass


class CoreListView(URLNameContextMixin, ListView):
    pass


class CoreFormView(URLNameContextMixin, FormView):
    pass
