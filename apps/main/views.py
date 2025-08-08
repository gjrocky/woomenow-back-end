# apps/main/views.py

import html

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.generic.edit import FormView
from wagtail.admin import messages

from apps.main.forms import SendEmailForm
from apps.main.helper import email_dict
from send_custom_email import send_db_email


class SendEmailAdminView(FormView):
    template_name = "wagtailadmin/generic/form.html"
    title = "Send Email"
    form_class = SendEmailForm
    submit_button_label = "Send Email"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_button_label"] = self.submit_button_label
        return context

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        restaurant = form.cleaned_data["restaurant"]
        influencer = form.cleaned_data["influencer"]
        manual_name = form.cleaned_data["manual_name"]
        manual_email = form.cleaned_data["manual_email"]
        template_obj = form.cleaned_data["template"]

        recipient_email = None
        recipient_name = None

        if user:
            recipient_email = [user.email]
            recipient_name = user.first_name or user.get_full_name() or "Guest"
        elif restaurant:
            recipient_email = [restaurant.email]
            recipient_name = strip_tags(html.unescape(restaurant.name))
        elif influencer:
            recipient_email = [influencer.email]
            recipient_name = influencer.name
        elif manual_name and manual_email:
            recipient_email = [manual_email]
            recipient_name = manual_name

        if not recipient_email:
            form.add_error(None, "No recipient email found.")
            return self.form_invalid(form)

        # Prepare inputs
        to_email = recipient_email
        template_enum = template_obj.template  # EmailTemplateType
        context_data = {
            "username": recipient_name,
            **email_dict,
        }

        # Call send_db_email
        send_db_email(to_email, template_enum, context_data)

        messages.success(
            self.request,
            f"Email sent to {recipient_email} using template '{template_obj.get_template_display()}'"
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):

        for error in form.non_field_errors():
            messages.error(self.request, error)

        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("send_email_admin")
