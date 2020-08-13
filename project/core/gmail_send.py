# https://realpython.com/python-send-email/
# run as cron job

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# converting this to import for cronjob based script
def send_mail(config, first, appt, rcvr):
    # login setup
    login_email = config['login']
    secret = config['secret']

    # email bits setup
    # TODO before going live the receiver email has to be matched to actual account
    # TODO currently it is only matched to my account
    sender_email = config['sndr']
    subject = "Your upcoming Portland IMT appointment"
    additional_text = "\nThis is an automated email; please do not reply."

    # plug in the bits to create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = rcvr
    message["Subject"] = subject
    # Add body to email
    body = f'Hi {first},\nYour appointment with Kellye is {appt} {additional_text}'
    message.attach(MIMEText(body, "plain"))

    # smtp server setup
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls, this has to match what you put in google when you set it up
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted?
            server.starttls(context = context)
            server.ehlo()  # Can be omitted?
            server.login(login_email, secret)
            server.sendmail(sender_email, rcvr, message.as_string())
    except Exception as e:
        print(e)


if __name__ == '__main__':
    send_mail()
