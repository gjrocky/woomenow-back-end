from django import forms

from apps.snippet.choices import EMAIL_TEMPLATE_CATEGORIES
from apps.snippet.models import EmailTemplate


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get used templates (excluding the current instance in edit mode)
        used_options = (
            EmailTemplate.objects
            .exclude(id=self.instance.id if self.instance and self.instance.pk else None)
            .values_list('template', flat=True)
            .distinct()
        )
        used_options = [str(opt).strip() for opt in used_options]

        # Build grouped & filtered choices
        filtered_choices = [("", "Please select an Email Template")]
        for group_label, options in EMAIL_TEMPLATE_CATEGORIES:
            available = [
                (value, label)
                for value, label in options
                if str(value).strip() not in used_options
            ]
            if available:
                filtered_choices.append((group_label, available))

        self.fields['template'].choices = filtered_choices

        if not filtered_choices:
            self.fields['template'].disabled = True
            self.fields['template'].help_text = _('No available email template types remain.')

    def clean_template(self):
        template = self.cleaned_data.get('template')

        # Double check uniqueness (in case two users save at same time)
        if EmailTemplate.objects.exclude(id=self.instance.id).filter(template=template).exists():
            raise forms.ValidationError(_("This email template type has already been used."))
        return template
