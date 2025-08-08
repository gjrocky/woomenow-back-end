from django.core.mail import EmailMessage
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.snippet.choices import EmailTemplateType
from apps.snippet.models import EmailTemplate
from woo_me_now_backend.utils.helpers import inject_icons_in_list_items, add_padding_to_p_before_ul_or_a


def send_db_email(to_email, template_type: EmailTemplateType, context_data: dict):
    try:
        # Get email template
        template = EmailTemplate.objects.get(template=template_type)
        front_end_link = context_data.get('front_end_link', '')
        icon = context_data.get('icon', '')

        subject = Template(template.subject).render(Context(context_data)).strip()

        # Render rich_body and optionally rich_lower_body
        html_body_top = Template(template.rich_body).render(Context(context_data))
        html_body_top = html_body_top.replace('https://placeholder.url/', front_end_link)
        html_body_top = inject_icons_in_list_items(html_body_top, icon)
        html_body_top = add_padding_to_p_before_ul_or_a(html_body_top)

        email_middle = ""
        html_body_lower = ""

        if template.rich_lower_body:
            # There is a hardcoded section
            email_middle = render_to_string(f"emails/middle_section/{template_type}.html", context_data)

            html_body_lower = Template(template.rich_lower_body).render(Context(context_data))
            html_body_lower = html_body_lower.replace('https://placeholder.url/', front_end_link)
            html_body_lower = inject_icons_in_list_items(html_body_lower, icon)
            html_body_lower = add_padding_to_p_before_ul_or_a(html_body_lower)

        # Combine all parts for rendering
        combined_body = html_body_top + email_middle + html_body_lower
        plain_body = strip_tags(combined_body)

        full_html = render_to_string("emails/base_email.html", {
            "subject": subject,
            "email_body": html_body_top,
            "email_middle": email_middle,
            "email_lower": html_body_lower,
            **context_data,
        })

        # Send email
        email = EmailMessage(
            subject=subject,
            body=full_html,
            from_email="himanshu.suchak@dcycle.design",
            to=to_email if isinstance(to_email, list) else [to_email],
            reply_to=["hr@dcycle.design"]
        )
        email.content_subtype = "html"
        email.send()

    except EmailTemplate.DoesNotExist:
        raise Exception(f"Email template '{template_type}' not found.")
