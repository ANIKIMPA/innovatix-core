from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from innovatix.core.admin import CoreAdmin
from innovatix.users.forms import CustomerUserChangeForm, CustomerUserCreationForm
from innovatix.users.models import Company, ContactModel, CustomerUser, Tag
from payments.admin import PaymentMethodInline
from products.admin import SubscriptionAdminInline

from .forms import CompanyAddForm


@admin.register(Company)
class CompanyAdmin(CoreAdmin):
    add_form = CompanyAddForm
    list_display = ["name", "city", "state", "country", "email"]
    search_fields = ["name", "city", "state", "country", "email"]
    list_filter = ["country", "state"]
    ordering = ["name"]


@admin.register(ContactModel)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone_number",
    )
    search_fields = (
        "name",
        "email",
        "phone_number",
    )

    def has_change_permission(
        self, request: HttpRequest, obj: ContactModel | None = None
    ) -> bool:
        return False


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("text",)
    ordering = ["text"]
    search_fields = ["text"]


@admin.register(CustomerUser)
class CustomerUserAdmin(UserAdmin):
    inlines = (
        SubscriptionAdminInline,
        PaymentMethodInline,
    )
    # Made 'add_form_template = None' to remove the default message on the admin template.
    add_form_template = None
    add_form = CustomerUserCreationForm
    form = CustomerUserChangeForm
    fieldsets = (
        (
            None,
            {"fields": ("external_customer_id", "partner_number", "email", "password")},
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "company",
                    "country",
                    "address1",
                    "address2",
                    "city",
                    "province",
                    "zip",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Marketing settings"),
            {
                "fields": ("accept_email_marketing", "accept_sms_marketing"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Other info"),
            {
                "fields": ("tags", "notes"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "company",
                    "address1",
                    "address2",
                    "city",
                    "country",
                    "province",
                    "zip",
                ),
            },
        ),
    )
    list_display = (
        "email",
        "display_full_name",
        "date_joined",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "is_active",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = (
        "-date_joined",
        "email",
        "first_name",
        "last_name",
    )
    filter_horizontal = ("tags",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            full_name=Concat(
                "first_name", Value(" "), "last_name", output_field=CharField()
            )
        )
        return queryset

    @admin.display(description="Full Name", ordering="full_name")
    def display_full_name(self, obj: CustomerUser):
        return obj.get_full_name()

    def get_readonly_fields(
        self, request: HttpRequest, obj: CustomerUser | None = None
    ) -> list[str]:
        if not obj:
            return []

        if obj and obj.pk == 1:
            return [
                "first_name",
                "last_name",
            ]

        return [
            "partner_number",
            "external_customer_id",
            "date_joined",
            "last_login",
        ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: CustomerUser | None = None
    ) -> bool:
        return False

    # @admin.action(permissions=["change"], description="Export selected customers")
    # def export_selected_objects(self, request, queryset):
    #     selected = queryset.values_list("pk", flat=True)
    #     ct = ContentType.objects.get_for_model(queryset.model)
    #     self.message_user(
    #         request,
    #         ngettext(
    #             "%d story was successfully marked as published.",
    #             "%d stories were successfully marked as published.",
    #             updated,
    #         )
    #         % updated,
    #         messages.SUCCESS,
    #     )

    #     return HttpResponseRedirect(
    #         "/export/?ct=%s&ids=%s"
    #         % (
    #             ct.pk,
    #             ",".join(str(pk) for pk in selected),
    #         )
    #     )
