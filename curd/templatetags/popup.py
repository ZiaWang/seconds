from django.template import Library
from django.urls import reverse

register = Library()


@register.inclusion_tag(filename='curd/form.html')
def form_popup(form_obj):
    from django.forms.models import ModelChoiceField
    new_form = []
    for bound_field in form_obj:  # django.forms.boundfield.BoundField
        temp = {"is_popup": False, "bound_field": bound_field}
        if isinstance(bound_field.field, ModelChoiceField):
            field_related_model_class = bound_field.field.queryset.model
            app_model = field_related_model_class._meta.app_label, field_related_model_class._meta.model_name
            base_url = reverse("curd:%s_%s_add" % app_model)
            popup_url = "%s?_popbackid=%s" % (base_url, bound_field.auto_id)
            temp["is_popup"] = True
            temp["popup_url"] = popup_url
        new_form.append(temp)
    return {"form": new_form}
