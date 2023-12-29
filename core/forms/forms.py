from django import forms
from django.db.models import Model


class CoreModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
                continue
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["style"] = "height: 12rem"
            elif hasattr(field.widget, "input_type"):
                field.widget.attrs["class"] = "form-control"

            field.widget.attrs["placeholder"] = field.label

            if self[field_name].errors:
                field.widget.attrs["class"] += " is-invalid"

    def cleaned_data_with_model_pk(self):
        user_info = self.cleaned_data.copy()
        for key, value in user_info.items():
            if isinstance(value, Model):
                # Replace model instance with its primary key
                user_info[key] = value.pk

        return user_info
