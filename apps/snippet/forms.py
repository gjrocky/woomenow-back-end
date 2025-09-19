from django import forms
from django.utils.translation import gettext_lazy as _

from apps.snippet.models import EmailTemplate, EmailTemplateChoice, EmailCategory


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Exclude template choices already used (except current instance in edit mode)
        used_choices = EmailTemplate.objects.exclude(
            id=self.instance.id if self.instance and self.instance.pk else None
        ).values_list('template_id', flat=True)

        # Build grouped choices from DB
        grouped_choices = [("", "Please select an Email Template")]
        for category in EmailCategory.objects.all():
            choices_in_category = EmailTemplateChoice.objects.filter(
                category=category
            ).exclude(id__in=used_choices)

            if choices_in_category.exists():
                options = [(c.id, c.label) for c in choices_in_category]
                grouped_choices.append((category.name, options))

        self.fields['template'].choices = grouped_choices

        if len(grouped_choices) == 1:  # only the placeholder
            self.fields['template'].disabled = True
            self.fields['template'].help_text = _('No available email template types remain.')

    def clean_template(self):
        template = self.cleaned_data.get('template')
        if EmailTemplate.objects.exclude(id=self.instance.id).filter(template=template).exists():
            raise forms.ValidationError(_("This email template type has already been used."))
        return template
