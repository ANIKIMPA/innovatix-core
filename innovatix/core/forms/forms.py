from django import forms


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
