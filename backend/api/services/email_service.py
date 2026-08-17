import smtplib
from email.message import EmailMessage

from django.conf import settings
from django.template.loader import render_to_string


class EmailService:
    """Service encapsulating email template rendering and SMTP dispatching."""

    @staticmethod
    def send_email_message(to_email, subject, text_body, html_content=None):
        """Builds and sends an email message via the configured SMTP backend."""
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = settings.DEFAULT_FROM_EMAIL
        message['To'] = to_email
        message.set_content(text_body)

        if html_content:
            message.add_alternative(html_content, subtype='html')

        smtp_host = settings.EMAIL_HOST
        smtp_port = settings.EMAIL_PORT
        smtp_username = settings.EMAIL_HOST_USER
        smtp_password = settings.EMAIL_HOST_PASSWORD
        use_tls = settings.EMAIL_USE_TLS
        use_ssl = settings.EMAIL_USE_SSL

        if use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if use_tls:
                    server.starttls()
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(message)

    @classmethod
    def send_verification_email(cls, to_email, username, verification_url):
        """Renders the account verification template and dispatches the email."""
        html_content = render_to_string('api/emails/verify_email.html', {
            'user': {'first_name': username},
            'verification_url': verification_url,
        })

        cls.send_email_message(
            to_email=to_email,
            subject='Verify your PREX account',
            text_body=f'Hi {username}, verify your email: {verification_url}',
            html_content=html_content,
        )

    @classmethod
    def send_password_reset_email(cls, to_email, username, reset_url):
        """Renders the password reset template and dispatches the email."""
        html_content = render_to_string('api/emails/reset_password.html', {
            'username': username,
            'reset_password_url': reset_url,
        })

        cls.send_email_message(
            to_email=to_email,
            subject='Reset your PREX password',
            text_body=f'Hi {username}, reset your password: {reset_url}',
            html_content=html_content,
        )


# Convenience module-level aliases
send_email_message = EmailService.send_email_message
send_verification_email = EmailService.send_verification_email
send_password_reset_email = EmailService.send_password_reset_email
