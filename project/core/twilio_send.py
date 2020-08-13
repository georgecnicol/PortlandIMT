# Download the helper library from https://www.twilio.com/docs/python/install
# pip3 install twilio
# run as cron job

from twilio.rest import Client


def twilio_contact(config, first, appt, phone):
    additional_text = 'This message is automated, please do not reply. Visit https://www.portlandimt.net or call 971-277-1855. Thanks and see you then!'
    account_sid = config.get('account_sid')
    auth_token = config.get('auth_token')
    from_ = config.get('phone')

    client = Client(account_sid, auth_token)
    body = f'Hi {first}, your appointment with Kellye is {appt} {additional_text}'
    to = f'+1{phone}'
    message = client.messages.create(
             body=body,
             from_=from_,
             to=to
         )
    # print(message.status)

