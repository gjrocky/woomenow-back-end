from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_email(emails, body, context, subject_context):
    subject = 'emails/subject/index.html'

    subject_template = render_to_string(subject, subject_context).strip()
    from_email = None

    body_template = render_to_string(body, context)

    email = EmailMessage(
        subject=subject_template,
        body=body_template,
        from_email=from_email,
        to=emails,
        reply_to=['hr@dcycle.design'],
    )

    email.content_subtype = 'html'
    email.send()