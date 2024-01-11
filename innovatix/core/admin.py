from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.utils.translation import gettext as _

from innovatix.core.forms import ReadOnlyField


class CoreAdmin(admin.ModelAdmin):
    add_fieldsets = None
    add_form = None

    def __init__(self, model: type, admin_site: AdminSite | None) -> None:
        super().__init__(model, admin_site)

        self.change_form = self.form

    def get_custom_readonly_fields(self, request, obj=None):
        return []

    def get_fieldsets(self, request, obj=None):
        if self.add_fieldsets and not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, change=False, **kwargs):
        if self.add_form and not obj:
            self.form = self.add_form
        else:
            self.form = self.change_form

        form = super().get_form(request, obj, change, **kwargs)

        for field in self.get_custom_readonly_fields(request, obj):
            content = getattr(obj, field["method_name"])() if obj else None
            form.base_fields[field["name"]] = ReadOnlyField(
                content=content,
                label=field["name"].replace("_", " ").capitalize(),
                help_text=field["help_text"].format(f"../../{obj.pk}"),
            )

        return form
