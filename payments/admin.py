from django.contrib import admin
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from payments.forms import PaymentForm, PaymentMethod
from payments.models import Payment


class PaymentMethodInline(admin.TabularInline):
    model = PaymentMethod
    extra = 0
    fields = (
        "display_card_number",
        "display_expires",
        "display_type",
        "card_name",
    )
    exclude = ("external_payment_method_id",)
    readonly_fields = (
        "display_expires",
        "display_card_number",
        "display_type",
        "card_name",
    )

    @admin.display(description=_("Card number"))
    def display_card_number(self, obj: PaymentMethod):
        return obj.get_display_card_number()

    @admin.display(description=_("Type"))
    def display_type(self, obj: PaymentMethod):
        return obj.get_display_type()

    @admin.display(description=_("Expires"))
    def display_expires(self, obj: PaymentMethod):
        return obj.get_display_expires()

    def has_change_permission(
        self, request: HttpRequest, obj: PaymentMethod | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: PaymentMethod | None = None
    ) -> bool:
        return False

    def has_add_permission(
        self, request: HttpRequest, obj: PaymentMethod | None = None
    ) -> bool:
        return False


class PaymentInline(admin.TabularInline):
    fields = (
        "get_display_total",
        "status",
        "description",
        "date",
        "payment_method",
    )
    readonly_fields = ("get_display_total",)
    show_change_link = True
    model = Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "external_payment_id",
                    "description",
                    "user_membership",
                    "date",
                    "get_display_total",
                    "status",
                )
            },
        ),
        (
            _("Payment Method"),
            {
                "fields": (
                    "payment_method__external_payment_method_id",
                    "payment_method__display_card_number",
                    "payment_method__display_expires",
                    "payment_method__display_type",
                    "payment_method__card_name",
                    "payment_method__user",
                )
            },
        ),
    )
    list_display = (
        "get_display_total",
        "status",
        "description",
        "user_membership",
        "date",
    )
    list_filter = (
        "status",
        "date",
    )
    ordering = (
        "-date",
        "total",
        "status",
    )
    readonly_fields = (
        "external_payment_id",
        "user_membership",
        "payment_method__external_payment_method_id",
        "payment_method__user",
        "payment_method__card_name",
        "payment_method__display_card_number",
        "payment_method__display_type",
        "payment_method__display_expires",
        "date",
        "get_display_total",
        "status",
    )

    @admin.display(description=_("Stripe ID"))
    def payment_method__external_payment_method_id(self, obj: Payment):
        if obj.has_payment_method():
            return obj.payment_method.external_payment_method_id
        return "-"

    @admin.display(description=_("Customer"))
    def payment_method__user(self, obj: Payment):
        if obj.has_payment_method() and obj.payment_method.user:
            url = reverse(
                "admin:users_customeruser_change",
                args=[obj.payment_method.user.id],
            )
            return format_html(
                '<a href="{}" title="See customer">{}</a>', url, obj.payment_method.user
            )
        return "-"

    @admin.display(description=_("Owner"))
    def payment_method__card_name(self, obj: Payment):
        if obj.has_payment_method():
            return obj.payment_method.card_name
        return "-"

    @admin.display(description=_("Number"))
    def payment_method__display_card_number(self, obj: Payment):
        if obj.has_payment_method():
            return obj.payment_method.get_display_card_number()
        return "-"

    @admin.display(description=_("Type"))
    def payment_method__display_type(self, obj: Payment):
        if obj.has_payment_method():
            return obj.payment_method.get_display_type()
        return "-"

    @admin.display(description=_("Expires"))
    def payment_method__display_expires(self, obj: Payment):
        if obj.has_payment_method():
            return obj.payment_method.get_display_expires()
        return "-"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
