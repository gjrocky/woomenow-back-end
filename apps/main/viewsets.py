# apps/main/viewsets.py
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import FormView
from wagtail.admin import messages
from wagtail.snippets.views.snippets import SnippetViewSet

from apps.main.forms import SendEmailForm
from send_custom_email import send_db_email


class SendEmailViewSet(SnippetViewSet, FormView):
    template_name = "wagtailadmin/generic/form.html"
    form_class = SendEmailForm
    icon = "mail"
    label = "sendemail"
    menu_label = "Send Email"
    base_url_path = "send-email"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(
            title="Send Email",
            form=self.get_form()
        ))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = form.cleaned_data["user"]
            template = form.cleaned_data["template"]
            send_db_email(user.email, template.subject, template.body)
            messages.success(request, f"Email sent to {user.email} using template '{template.title}'")
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(
            title="Send Email",
            form=form
        ))

    def get_success_url(self):
        return reverse("wagtailsnippets_sendemail:index")
