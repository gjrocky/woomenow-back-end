import html

from django import forms
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags

from apps.main.models import Restaurant, Influencer
from apps.snippet.models import EmailTemplate

User = get_user_model()


class SendEmailForm(forms.Form):
    user = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.all(),
        label="User",
        widget=forms.Select,
        help_text="Select a user to send email to.",
    )
    restaurant = forms.ChoiceField(
        required=False,
        label="Restaurant/Experience",
        widget=forms.Select,
        help_text="Select a restaurant/experience to send email to.",
    )
    influencer = forms.ModelChoiceField(
        required=False,
        queryset=Influencer.objects.all(),
        label="Influencer",
        widget=forms.Select,
        help_text="Select a influencer to send email to.",
    )
    manual_name = forms.CharField(
        required=False,
        label="Business Name",
        help_text="Enter name of restaurant/experience or influencer you want to invite or send email",
    )
    manual_email = forms.EmailField(
        required=False,
        label="Business Email",
        help_text="Enter email of the restaurant/experience or influencer you want to invite or send email."
    )
    template = forms.ModelChoiceField(
        required=True,
        queryset=EmailTemplate.objects.all(),
        label="Email Template",
        widget=forms.Select,
        help_text="Select an email template."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show user's full name + email in the dropdown
        self.fields["user"].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.email})"

        # Group restaurants by type (RestaurantType.choices)
        grouped_choices = []

        for type_value, type_label in Restaurant._meta.get_field("type").choices:
            restaurants = Restaurant.objects.filter(type=type_value)
            if restaurants.exists():
                grouped_choices.append((
                    type_label,  # This becomes the optgroup label
                    [(r.id, f"{strip_tags(html.unescape(r.name))} ({r.email})" if r.email else strip_tags(
                        html.unescape(r.name))) for r in restaurants]
                ))

        self.fields["restaurant"].choices = [("", "---------")] + grouped_choices

    def clean(self):
        cleaned_data = super().clean()
        user = self.cleaned_data.get("user")
        restaurant = self.cleaned_data.get("restaurant")
        influencer = self.cleaned_data.get("influencer")
        manual_name = self.cleaned_data.get("manual_name")
        manual_email = self.cleaned_data.get("manual_email")

        # Check if manual entry is being used (both name and email must be provided)
        manual_entry = manual_name and manual_email

        # Count how many options are selected
        selected_options = sum([
            bool(user),
            bool(restaurant),
            bool(influencer),
            bool(manual_entry)
        ])

        if selected_options == 0:
            self.add_error(None,
                           "Please select either a User, Restaurant, Influencer, or provide both Business Name and Email.")
        elif selected_options > 1:
            self.add_error(None,
                           "Please select only one option: either a User, Restaurant, Influencer, or Business entry (not multiple).")

        # Validate manual entry fields individually
        if manual_email and not manual_name:
            self.add_error("manual_name", "You must provide a business name when specifying an email address.")
        elif manual_name and not manual_email:
            self.add_error("manual_email", "You must provide an email address when specifying a business name.")

        return cleaned_data
