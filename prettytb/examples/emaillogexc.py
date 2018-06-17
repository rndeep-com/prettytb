# -*- coding: utf-8 -*-
"""
    Example child class of `logexc`.

    Before usage the `emaillogexc` class must be configured as outlined below.

    Configuration:
        >>> from prettytb.examples.emaillogexc import emaillogexc
        >>> emaillogexc.FROM_EMAIL = <<YOUR-EMAIL>>
        >>> emaillogexc.FROM_PASSWORD = <<YOUR-PASSWORD>>
        >>> emaillogexc.TO_EMAILS = [<<SOMEONES-EMAIL-ADDRESS>>]

    Usage:
        >>> with emaillogexc():
        >>>     1/0
"""

from datetime import datetime
import getpass
import platform
import smtplib
from prettytb import logexc


class emaillogexc(logexc):
    """
        Like logexc but also sends out an email with the resulting error report.

        Note that the class attributes `FROM_EMAIL`, `FROM_PASSWORD`, `TO_EMAILS`
        should be set before.

        Attributes:
            FROM_EMAIL (str): The sender's email address.
            FROM_PASSWORD (str): The sender's email account password.
            TO_EMAILS (:obj:`list`): List of `str` recipient email addresses.
                When an exception is caught those users will be informed.
    """

    FROM_EMAIL = None
    FROM_PASSWORD = None
    TO_EMAILS = []
    SMTP_ADDRESS = 'smtp.gmail.com'

    def __init__(self, *a, **kwa):
        logexc.__init__(self, *a, **kwa)
        self._validate_settings()

    def _validate_settings(self):
        if self.FROM_EMAIL is None:
            raise ValueError('emaillogexc.FROM_EMAIL not set.')
        if self.FROM_PASSWORD is None:
            raise ValueError('emaillogexc.FROM_PASSWORD not set.')
        if self.TO_EMAILS == []:
            raise ValueError('emaillogexc.TO_EMAILS not set.')

    def handle_error_report(self, exception, error_message, error_report):
        """ Logs the report and then sends out an e-mail containing the report. """

        logexc.handle_error_report(self, exception, error_message, error_report)
        self._send_email(exception, error_report)

    def _send_email(self, exception, error_report):
        try:
            email_body = self._get_email_body(exception, error_report)
            server = smtplib.SMTP_SSL(self.SMTP_ADDRESS, 465)
            server.ehlo()
            server.login(self.FROM_EMAIL, self.FROM_PASSWORD)
            to_emails_string = ", ".join(self.TO_EMAILS)
            server.sendmail(self.FROM_EMAIL, to_emails_string, email_body)
            server.close()
        except Exception as exc:
            print('Error sending error report e-mail.')
            print("{exc.__class__.__name__}: {exc}".format(exc=exc))
            raise

    def _get_email_body(self, exception, error_report):
        timestamp = datetime.now().strftime('%H-%M-%S')
        hostname = platform.node()
        user_login = getpass.getuser()

        to_emails_string = ", ".join(self.TO_EMAILS)
        subject = "[Unexpected Exception]: {0} {1} {2} {3}".format(exception, user_login, hostname, timestamp)
        body = r"""
From: {0}
To: {1}
Subject: {2}

{3}
"""[1:-1].format(self.FROM_EMAIL, to_emails_string, subject, error_report)
        return body

