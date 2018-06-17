"""
    Tests the `emaillogexc` function which sends out e-mails with the error report.

    NOTE: The email tests are commented out as they need user credentials to work(edit the code below to test it).
"""

from prettytb.examples import emaillogexc


# def setup_module():
#     import os
#     os.environ['USERNAME'] = 'someuser'
#
#     emaillogexc.FROM_EMAIL = '<<<YOUR-EMAIL>>>@gmail.com'
#     emaillogexc.FROM_PASSWORD = '<<<YOUR-PASSWORD>>>'
#     emaillogexc.TO_EMAILS = ['<<<TARGET-EMAIL>>>@gmail.com']
#
# def test_email():
#     with emaillogexc():
#         1/0
