import statistics
from typing import Any

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.http.request import HttpRequest
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.urls.resolvers import URLPattern
from django.utils.decorators import method_decorator
from django.utils.html import escape, format_html
from django.utils.safestring import SafeText
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django.views.decorators.debug import sensitive_post_parameters
from django_summernote.admin import SummernoteModelAdmin
from innovatix.core.admin import CoreAdmin
from payments.admin import PaymentInline
from products.constants import ENTRY_COST_HELP_TEXT, RECURRING_PRICE_HELP_TEXT
from products.forms import (
    MembershipAddForm,
    MembershipChangeForm,
    MembershipPriceChangeForm,
    UpdateSubscriptionPriceForm,
)
from products.models import Membership, UserMembership
from products.services import payment_gateway

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class UserMembershipInline(admin.StackedInline):
    show_change_link = True
    model = UserMembership
    extra = 0
    fields = (
        "user",
        "membership",
        "date_subscribed",
        "status",
        "get_next_billing_date",
    )
    readonly_fields = ("get_next_billing_date",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_filter = ("status",)
    fields = (
        "external_subscription_id",
        "user",
        "membership_name",
        "display_recurring_price",
        "date_subscribed",
        "status",
        "get_next_billing_date",
    )
    list_display = (
        "user",
        "status",
        "membership_name",
        "display_recurring_price",
        "date_subscribed",
    )
    inlines = (PaymentInline,)
    actions = ["update_price"]

    @admin.display(description="Recurring price", ordering="recurring_price")
    def display_recurring_price(self, obj):
        return obj.get_display_recurring_price()

    @admin.display(description="Membership", ordering="membership")
    def membership_name(self, obj):
        return obj.membership.name

    def has_delete_permission(
        self, request: HttpRequest, obj: UserMembership | None = None
    ) -> bool:
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: UserMembership | None = None
    ) -> bool:
        return False

    @admin.display(description="Update price for selected subscriptions")
    def update_price(
        self, request: HttpRequest, queryset: QuerySet[UserMembership]
    ) -> HttpResponseRedirect | HttpResponse:
        # Sets the initial value of "new_price" to the mode (most frequently occurring value)
        # of the recurring prices from the selected queryset of instances.
        initial = {
            "new_price": statistics.mode(
                [instance.get_recurring_price() for instance in queryset]
            )
        }
        form = UpdateSubscriptionPriceForm(initial=initial)

        if "apply" in request.POST:
            form = UpdateSubscriptionPriceForm(request.POST)

            if form.is_valid():
                new_price = int(form.cleaned_data.get("new_price") * 100)
                new_interval = form.cleaned_data.get("new_interval")

                count = 0
                for subscription in queryset:
                    subscription.recurring_price = new_price
                    subscription.recurring_payment = new_interval
                    result = payment_gateway.update_subscription(subscription)

                    if result:
                        subscription.save()
                        count += 1

                self.message_user(
                    request,
                    ngettext(
                        "%d subscription was successfully updated.",
                        "%d subscriptions were successfully updated.",
                        count,
                    )
                    % count,
                    messages.SUCCESS if count >= 1 else messages.ERROR,
                )
                return HttpResponseRedirect(request.get_full_path())

        item = {
            "verbose_name": queryset.model._meta.verbose_name,
            "verbose_name_plural": queryset.model._meta.verbose_name_plural,
        }

        action = _("update_price")

        return render(
            request,
            "admin/products/subscription/update_price.html",
            context={
                "queryset": queryset,
                "form": form,
                "item": item,
                "action": action,
                "title": action.replace("_", " ").capitalize(),
                "help_text": _(
                    "Enter the <strong>new price</strong> and <strong>recurring interval</strong> you want to apply on the selected subscriptions:"
                ),
            },
        )


@admin.register(Membership)
class MembershipAdmin(CoreAdmin, SummernoteModelAdmin):
    add_form = MembershipAddForm
    form = MembershipChangeForm
    change_prices_form = MembershipPriceChangeForm
    search_fields = (
        "name",
        "recurring_payment",
    )
    list_display = (
        "name",
        "display_recurring_price",
        "display_entry_cost",
        "subscription_count_link",
        "is_visible",
        "is_purchasable",
    )
    list_display_links = ("name",)
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "entry_cost",
                    "recurring_price",
                    "recurring_payment",
                    "is_visible",
                    "is_purchasable",
                )
            },
        ),
        (_("Description"), {"fields": ("short_description", "long_description")}),
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "external_product_id",
                    "name",
                    "slug",
                    "entry_cost",
                    "recurring_price",
                    "is_visible",
                    "is_purchasable",
                    "subscription_count_link",
                )
            },
        ),
        (_("Description"), {"fields": ("short_description", "long_description")}),
    )
    prepopulated_fields = {"slug": ("name",)}
    summernote_fields = (
        "short_description",
        "long_description",
    )
    list_filter = (
        "is_visible",
        "is_purchasable",
        "created_at",
    )
    save_on_top = True
    ordering = ("name",)

    @admin.display(description="Recurring price", ordering="recurring_price")
    def display_recurring_price(self, obj: Membership):
        return obj.get_display_recurring_price()

    @admin.display(description="Entry cost", ordering="entry_cost")
    def display_entry_cost(self, obj: Membership) -> Any:
        return obj.get_display_entry_cost()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request)
        return queryset.annotate(_subscription_count=Count("usermembership"))

    @admin.display(description="Subscriptions", ordering="_subscription_count")
    def subscription_count_link(self, obj) -> SafeText:
        count = obj._subscription_count
        url = (
            reverse("admin:products_usermembership_changelist")
            + f"?status__exact=active&membership__id={obj.pk}"
        )
        return format_html(
            '<a href="{}" title="Show subscriptions">{} active</a>', url, count
        )

    def get_custom_readonly_fields(
        self, request: HttpRequest, obj: Membership | None = None
    ) -> list[Any] | list[dict[str, str]]:
        if not obj:
            return []

        return [
            {
                "name": "recurring_price",
                "method_name": "get_display_recurring_price",
                "help_text": RECURRING_PRICE_HELP_TEXT
                + _(
                    ' To update this price, please <a href="{}/prices/">click here</a>.'
                ),
            },
            {
                "name": "entry_cost",
                "method_name": "get_display_entry_cost",
                "help_text": ENTRY_COST_HELP_TEXT
                + _(
                    ' To change this price, please <a href="{}/prices/">click here</a>.'
                ),
            },
        ]

    def get_readonly_fields(
        self, request: HttpRequest, obj: Membership | None = None
    ) -> list[Any] | list[str]:
        if not obj:
            return []

        return [
            "external_product_id",
            "subscription_count_link",
        ]

    def get_urls(self) -> list[URLPattern]:
        return [
            path(
                "<id>/prices/",
                self.admin_site.admin_view(self.membership_change_price),
                name="membership_price_change",
            ),
        ] + super().get_urls()

    def has_delete_permission(
        self, request: HttpRequest, obj: Membership | None = None
    ) -> bool:
        if obj:
            return not obj.is_linked_to_subscriptions()
        return super().has_delete_permission(request, obj)

    def delete_model(self, request: HttpRequest, obj: Membership) -> None:
        # Call the delete_membership method before deleting the object
        payment_gateway.delete_membership(obj)
        super().delete_model(request, obj)

    @sensitive_post_parameters_m
    def membership_change_price(
        self, request: HttpRequest, id: str, form_url: str = ""
    ) -> HttpResponseRedirect | TemplateResponse:
        membership = self.get_object(request, unquote(id))

        if not self.has_change_permission(request, membership):
            raise PermissionDenied
        if membership is None:
            raise Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {
                    "name": self.opts.verbose_name,
                    "key": escape(id),
                }
            )

        if request.method == "POST":
            form = self.change_prices_form(request.POST, instance=membership)

            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, membership, change_message)
                msg = gettext("Price changed successfully.")
                messages.success(request, msg)
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_change"
                        % (
                            self.admin_site.name,
                            membership._meta.app_label,
                            membership._meta.model_name,
                        ),
                        args=(membership.pk,),
                    )
                )
        else:
            form = self.change_prices_form(instance=membership)

        fieldsets = [(None, {"fields": (list(form.base_fields))})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Change price: %s") % escape(membership.name),
            "adminForm": admin_form,
            "form_url": form_url,
            "form": form,
            "is_popup": (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            "is_popup_var": IS_POPUP_VAR,
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.opts,
            "original": membership,
            "save_as": False,
            "show_save": True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        if "jazzmin" in settings.INSTALLED_APPS:
            change_membership_prices_template = (
                "admin/products/membership/change_prices_jazzmin.html"
            )
        else:
            change_membership_prices_template = (
                "admin/products/membership/change_prices.html"
            )

        return TemplateResponse(
            request,
            change_membership_prices_template,
            context,
        )
