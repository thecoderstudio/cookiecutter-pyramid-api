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
        self.account_verification_template_id = sendgrid_settings[
            'account_verification_template_id']

    def send_account_recovery_email(self, recipient_email_address: str,
                                    password_reset_token: str):
        return self._send_secure_token_email(
            recipient_email_address,
            password_reset_token,
            self.account_recovery_template_id
        )

    def send_account_verification_email(self, recipient_email_address: str,
                                        verification_token: str):
        return self._send_secure_token_email(
            recipient_email_address,
            verification_token,
            self.account_verification_template_id
        )

    def _send_secure_token_email(self,
                                 recipient_email_address: str,
                                 token: str,
                                 template_id: str):
        message = Mail(
            from_email=self.sender_email_address,
            to_emails=recipient_email_address
        )
        message.template_id = template_id
        message.dynamic_template_data = {
            'token': token
        }

        response = self.client.send(message)
        return response.status_code == HTTPStatus.CREATED
