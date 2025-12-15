# apps/main/views.py

import html
import logging
import uuid
from urllib.parse import unquote

from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.generic.edit import FormView
from wagtail.admin import messages

from apps.main.forms import SendEmailForm
from apps.main.helper import email_dict
from apps.main.models import EmailExecution, Restaurant
from apps.main.tasks import send_restaurant_email_step
from send_custom_email import send_db_email

logger = logging.getLogger(__name__)


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
        recipient_email, recipient_name, invited_by = self.get_recipient(form)
        if not recipient_email:
            form.add_error(None, "No recipient email found.")
            return self.form_invalid(form)

        template_obj = form.cleaned_data.get("template")  # EmailTemplate instance

        context_data = {"username": recipient_name, **email_dict}
        if invited_by:
            context_data["influencer_name"] = invited_by

        execution_id = str(uuid.uuid4())

        try:
            send_db_email(recipient_email, template_obj.template, context_data, execution_id,
                          settings.EMAIL_WOO_ME_NOW_NO_REPLY_EMAIL)
            logger.info(
                f"[Admin] Manual email sent: '{template_obj.name}' (ID: {template_obj.template.choice_id}) to "
                f"{recipient_email}")
        except Exception as e:
            logger.error(f"[Admin] Failed to send manual email: {e}")
            form.add_error(None, f"Failed to send email: {e}")
            return self.form_invalid(form)

        # Create execution record
        category_slug = template_obj.template.category.slug
        execution = EmailExecution.objects.create(
            execution_id=execution_id,
            recipient_email=recipient_email[0],
            recipient_name=recipient_name,
            current_step=1,
            execution_flow=category_slug,
            last_sent_at=timezone.now(),
            last_sent_template_id=template_obj.template.choice_id,
        )
        logger.info(f"[Admin] Created EmailExecution {execution.execution_id} for {recipient_email[0]} | "
                    f"Manual email sent: DB Index {template_obj.template.choice_id}")

        # Schedule automation based on flow
        countdown_seconds = 5 * 60  # testing: 1 min; production: 24*60*60
        if category_slug == "restaurant-and-experience-onboarding-playbook":
            send_restaurant_email_step.apply_async(
                args=(str(execution.execution_id), 2),
                countdown=countdown_seconds
            )
            logger.info(f"[Admin] Step 2 scheduled for execution_id={execution.execution_id} in {countdown_seconds}s")

        else:
            logger.warning(
                f"Unknown flow '{category_slug}' for execution {execution.execution_id}. No automation scheduled.")

        messages.success(
            self.request,
            f"Email sent to {recipient_email} using template '{template_obj.name}'"
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)
            logger.error(f"Form error: {error}")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("send_email_admin")

    def get_recipient(self, form):
        """Determine recipient email and name from form."""
        user = form.cleaned_data.get("user")
        restaurant = form.cleaned_data.get("restaurant")
        influencer = form.cleaned_data.get("influencer")
        manual_name = form.cleaned_data.get("manual_name")
        manual_email = form.cleaned_data.get("manual_email")

        recipient_email = None
        recipient_name = None
        invited_by = None

        if user:
            recipient_email = [user.email]
            recipient_name = user.first_name or user.get_full_name() or "Guest"
        elif restaurant:
            restaurant_obj = Restaurant.objects.get(id=restaurant)
            recipient_email = [restaurant_obj.email]
            recipient_name = strip_tags(html.unescape(restaurant_obj.name))
            if restaurant_obj.invited_by:
                invited_by = strip_tags(html.unescape(restaurant_obj.invited_by.name))
        elif influencer:
            recipient_email = [influencer.email]
            recipient_name = influencer.name
        elif manual_name and manual_email:
            recipient_email = [manual_email]
            recipient_name = manual_name

        return recipient_email, recipient_name, invited_by


def track_email_link(request, execution_id):
    """
    Track email opens and redirect to the intended URL
    """
    try:
        # Log the tracking attempt
        logger.info(f"Email tracking attempt for execution_id: {execution_id}")

        # Get the execution record
        execution = get_object_or_404(EmailExecution, execution_id=execution_id)

        # Mark as opened if not already marked
        if not execution.is_opened:
            execution.is_opened = True
            execution.save(update_fields=["is_opened"])
            logger.info(f"Marked email as opened for execution_id: {execution_id} (first time)")
        else:
            logger.info(f"Email already marked as opened for execution_id: {execution_id} link clicked again")

        # Get redirect URL from query parameters
        redirect_url = request.GET.get('redirect', '/')

        if not redirect_url:
            logger.warning(f"No redirect URL provided for execution_id: {execution_id}")
            return HttpResponseBadRequest("No redirect URL provided")

        # Decode the URL-encoded redirect parameter
        decoded_redirect_url = unquote(redirect_url)

        logger.info(f"Redirecting to: {decoded_redirect_url} for execution_id: {execution_id}")

        return redirect(decoded_redirect_url)

    except EmailExecution.DoesNotExist:
        logger.error(f"EmailExecution not found for execution_id: {execution_id}")
        return redirect('/')
    except Exception as e:
        logger.error(f"Error in email tracking for execution_id {execution_id}: {str(e)}")
        return redirect('/')
