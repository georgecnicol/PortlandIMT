# Download the helper library from https://www.twilio.com/docs/python/install
# pip3 install twilio
# $pip3 install apscheduler
# run as cron job

from project import get_config
from twilio.rest import Client
from project.appointments.apt_creator import make_reminder_list


def twilio_contact():
    additional_text = 'This message is automated, please do not reply. Visit https://www.example.com or call xxx-xxx-xxxx. Thanks and see you then!'
    config = get_config()
    account_sid = config.get('account_sid')
    auth_token = config.get('auth_token')
    from_ = config.get('phone')

    client = Client(account_sid, auth_token)
    for person, appt in make_reminder_list():
        if person.text_me == 1:
            body = f'Hi {person.first}, your appointment with Kellye is {str(appt)} {additional_text}'
            to = f'+1{person.phone}'
            message = client.messages \
                .create(
                     body=body,
                     from_=from_,
                     to=to
                 )
            print(message.status)


if __name__ == '__main__':
    twilio_contact()
