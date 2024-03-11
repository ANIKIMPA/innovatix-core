from django import forms
from django.utils.translation import gettext_lazy as _


class ReadOnlyWidget(forms.Widget):
    template_name = "core/widgets/read_only.html"
    read_only = True

    def id_for_label(self, id_):
        return None


class ReadOnlyField(forms.Field):
    widget = ReadOnlyWidget

    def __init__(self, content=None, *args, **kwargs):
        self.content = content
        kwargs.setdefault("required", False)
        kwargs.setdefault("disabled", True)
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if isinstance(widget, ReadOnlyWidget):
            if self.content is not None:
                attrs["content"] = self.content
        return attrs
