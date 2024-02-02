from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from innovatix.users.forms import CustomerUserChangeForm, CustomerUserCreationForm
from innovatix.users.models import ContactModel, CustomerUser, ProgramUser, Tag


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
class CoreTagAdmin(admin.ModelAdmin):
    list_display = ("text",)
    ordering = ["text"]
    search_fields = ["text"]


@admin.register(CustomerUser)
class CoreCustomerUserAdmin(UserAdmin):
    # Made 'add_form_template = None' to remove the default message on the admin template.
    add_form_template = None
    add_form = CustomerUserCreationForm
    form = CustomerUserChangeForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "external_customer_id",
                    "partner_number",
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                )
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "country",
                    "address1",
                    "address2",
                    "city",
                    "province",
                    "zip",
                )
            },
        ),
        (
            _("Marketing settings"),
            {"fields": ("accept_email_marketing", "accept_sms_marketing")},
        ),
        (_("Other info"), {"fields": ("tags", "notes")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
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
    list_display = ("email", "display_full_name", "date_joined", "is_active")
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
        self, request: HttpRequest, obj: CustomerUser | None
    ) -> list[str]:
        if not obj:
            return []

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


@admin.register(ProgramUser)
class ProgramUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone_number")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("collapsed",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = ("display_full_name", "email", "is_staff")
    search_fields = ("first_name", "last_name", "email")
    ordering = (
        "first_name",
        "last_name",
        "email",
    )
    readonly_fields = (
        "last_login",
        "date_joined",
    )
    model = ProgramUser

    @admin.display(description="Full Name", ordering="full_name")
    def display_full_name(self, obj: CustomerUser):
        return obj.get_full_name()

    def get_readonly_fields(
        self, request: HttpRequest, obj: ProgramUser | None = None
    ) -> list[str] | tuple[Any, ...]:
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.pk == 1:
            readonly_fields += (
                "first_name",
                "last_name",
            )

        return readonly_fields

    def has_delete_permission(
        self, request: HttpRequest, obj: ProgramUser | None = None
    ) -> bool:
        if obj and obj.pk == 1:
            return False

        return super().has_delete_permission(request, obj)
