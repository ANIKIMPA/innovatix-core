from typing import Any

from django.conf import settings
from django.http import HttpRequest


def company_info(request: HttpRequest) -> dict[str, Any]:
    return {
        "url_name": request.resolver_match.url_name,
        "company_name": settings.COMPANY_NAME,
        "company_phone": settings.COMPANY_PHONE,
        "company_email": settings.EMAIL_HOST_USER,
    }
