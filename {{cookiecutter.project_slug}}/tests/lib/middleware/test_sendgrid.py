from http import HTTPStatus

import pytest
from sendgrid.helpers.mail import Mail

from {{cookiecutter.project_slug}}.lib.middleware.sendgrid import SendGridClient


class MailMatcher:
    """Used to assert a Mail object for validity."""
    def __init__(
        self,
        sender_email_address: str,
        recipient_email_address: str,
        template_id: str,
        token: str
    ):
        self.recipient_email_address = recipient_email_address
        self.sender_email_address = sender_email_address
        self.template_id = template_id
        self.token = token

    def __eq__(self, mail: Mail):
        if mail.template_id.get() != self.template_id:
            return False

        if mail.from_email.get()['email'] != self.sender_email_address:
            return False

        personalization = mail.personalizations[0]

        to_emails = personalization.tos
        if (len(to_emails) != 1 or
                to_emails[0]['email'] != self.recipient_email_address):
            return False

        if personalization.dynamic_template_data.get('token') != self.token:
            return False

        return True


@pytest.mark.parametrize('result_status_code', (
    HTTPStatus.CREATED,
    HTTPStatus.INTERNAL_SERVER_ERROR
))
def test_sendgrid_send_account_recovery_email(mocker, result_status_code):
    sender_email_address = '{{cookiecutter.test_email_address}}'
    recipient_email_address = '{{cookiecutter.alternative_test_email_address}}'
    template_id = 'templateid'
    token = '123456'

    expected_result = False
    if result_status_code == HTTPStatus.CREATED:
        expected_result = True

    mocker.patch('{{cookiecutter.project_slug}}.lib.middleware.sendgrid.settings', {
        'sendgrid': {
            'sender_email_address': sender_email_address,
            'api_key': 'fake',
            'account_recovery_template_id': template_id
        }
    })

    response_mock = mocker.MagicMock()
    response_mock.status_code = result_status_code
    send_mock = mocker.patch(
        '{{cookiecutter.project_slug}}.lib.middleware.sendgrid.SendGridAPIClient.send',
        return_value=response_mock
    )

    result = SendGridClient().send_account_recovery_email(
        recipient_email_address,
        token
    )

    assert result == expected_result
    send_mock.assert_called_with(MailMatcher(
        sender_email_address,
        recipient_email_address,
        template_id,
        token
    ))
