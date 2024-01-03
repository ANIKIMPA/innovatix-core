import geoip2.database
from django.conf import settings
from django.core.exceptions import PermissionDenied


class GeoIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geo_reader = geoip2.database.Reader("resources/geolite2-country.mmdb")

    def __call__(self, request):
        if settings.ENVIRONMENT == "dev" or settings.TESTING:
            # Bypass IP check on dev environment and when testing.
            return self.get_response(request)

        # Get the client's IP address from the request object
        client_ip = self.get_client_ip(request)

        # Look up the client's geographic information
        try:
            response = self.geo_reader.country(client_ip)
            country = response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            # Handle IP not found in the database
            country = None

        # Check if the client is from an allowed country
        if country not in settings.ALLOWED_COUNTRIES:
            raise PermissionDenied  # Blocks access for clients outside the allowed countries

        # Otherwise, continue processing the request
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
