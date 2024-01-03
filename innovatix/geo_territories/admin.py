from django.contrib import admin
from django.http.request import HttpRequest

from innovatix.geo_territories.models import Country, Province


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Country | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Country | None = None
    ) -> bool:
        return False

    def has_view_permission(
        self, request: HttpRequest, obj: Country | None = None
    ) -> bool:
        return False


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Province | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Province | None = None
    ) -> bool:
        return False

    def has_view_permission(
        self, request: HttpRequest, obj: Province | None = None
    ) -> bool:
        return False
