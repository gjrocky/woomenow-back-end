import logging
import re
from smtplib import SMTPAuthenticationError, SMTPException

from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Template, Context
from django.template.loader import render_to_string

from apps.snippet.models import EmailTemplate
from woo_me_now_backend.utils.helpers import replace_tracking_link, replace_restaurant_id_and_respond_link, \
    inject_icons_in_list_items, add_padding_to_p_before_ul_or_a, style_otp

logger = logging.getLogger(__name__)


def send_db_email(to_email, template_type, context_data: dict, execution_id=None, from_email=None):
    try:
        # Get email template
        template = EmailTemplate.objects.get(template=template_type)
        icon = context_data.get("icon", "")
        front_end_link = context_data.get("front_end_link")

        subject = Template(template.subject).render(Context(context_data)).strip()

        def process_html_body(html_content: str) -> str:
            category_slug = getattr(
                getattr(getattr(template, "template", None), "category", None),
                "slug",
                None
            )

            if category_slug == "restaurant-and-experience-onboarding-playbook":
                if getattr(template, "has_tracking_link", False) and execution_id:
                    html_content = re.sub(
                        r'href="([^"]+)"',
                        lambda m: replace_tracking_link(m, front_end_link, execution_id),
                        html_content
                    )

            elif category_slug == "negative-review-flow":
                html_content = replace_restaurant_id_and_respond_link(
                    html_content, context_data, execution_id, front_end_link
                )

            html_content = re.sub(
                r"https?://woomenow\.com/?",
                front_end_link.rstrip("/") + "/",
                html_content
            )

            html_content = inject_icons_in_list_items(html_content, icon)
            html_content = add_padding_to_p_before_ul_or_a(html_content)
            html_content = style_otp(html_content)
            return html_content

        html_body_top = Template(template.rich_body).render(Context(context_data))
        html_body_top = process_html_body(html_body_top)

        email_middle = ""
        try:
            email_middle = render_to_string(f"emails/middle_section/{template_type}.html", context_data)
        except Exception:
            email_middle = ""

        html_body_lower = ""

        if template.rich_lower_body:
            html_body_lower = Template(template.rich_lower_body).render(Context(context_data))
            html_body_lower = process_html_body(html_body_lower)

        full_html = render_to_string(
            "emails/base_email.html",
            {
                "subject": subject,
                "email_body": html_body_top,
                "email_middle": email_middle,
                "email_lower": html_body_lower,
                **context_data,
            },
        )

        final_from_email = from_email or settings.DEFAULT_FROM_EMAIL

        if final_from_email in [settings.DEFAULT_FROM_EMAIL, settings.EMAIL_WOO_ME_NOW_NO_REPLY_EMAIL]:
            final_reply_to = [settings.EMAIL_WOO_ME_NOW_CONTACT_EMAIL]
        else:
            final_reply_to = [final_from_email]

        # Send email
        email = EmailMessage(
            subject=subject,
            body=full_html,
            from_email=final_from_email,
            to=to_email if isinstance(to_email, list) else [to_email],
            reply_to=final_reply_to
        )
        email.content_subtype = "html"
        email.send()

    except EmailTemplate.DoesNotExist:
        logger.error(f"Email template '{template_type}' not found.")
        raise Exception(f"Email template '{template_type}' not found.")

    except SMTPAuthenticationError:
        logger.error('SMTP Authentication failed', exc_info=True)
        raise Exception('Email service authentication failed.')

    except SMTPException:
        logger.error('SMTP Error while sending email', exc_info=True)
        raise Exception('Email service error while sending email.')

    except Exception:
        logger.error('Unexpected error while sending email', exc_info=True)
        raise Exception('Failed to send email.')
