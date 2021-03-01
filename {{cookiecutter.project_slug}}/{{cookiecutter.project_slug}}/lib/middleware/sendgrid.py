from http import HTTPStatus

from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

from {{cookiecutter.project_slug}}.lib.settings import settings


class SendGridClient:
    def __init__(self):
        sendgrid_settings = settings['sendgrid']
        self.sender_email_address = sendgrid_settings['sender_email_address']
        self.client = SendGridAPIClient(sendgrid_settings['api_key'])
        self.account_recovery_template_id = sendgrid_settings[
            'account_recovery_template_id']

    def send_account_recovery_email(self, recipient_email_address: str,
                                    password_reset_token: str):
        message = Mail(
            from_email=self.sender_email_address,
            to_emails=recipient_email_address
        )
        message.template_id = self.account_recovery_template_id
        message.dynamic_template_data = {
            'token': password_reset_token
        }

        response = self.client.send(message)
        return response.status_code == HTTPStatus.CREATED
