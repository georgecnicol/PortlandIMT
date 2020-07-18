# https://realpython.com/python-send-email/
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from project.appointments.apt_creator import make_reminder_list


def send_mail():
    # login setup
    # TODO - change to env variable in prod?
    with open('/Users/admin/website/gmail.txt', 'r') as fh:
        details = fh.read().split()
    login_email = details[0]
    secret = details[1]

    # email bits setup
    # TODO before going live the receiver email has to be matched to actual account
    # TODO currently it is only matched to my account
    receiver_email = details[3]
    sender_email = details[2]
    subject = "Your upcoming Portland IMT appointment"
    additional_text = "\nThis is an automated email; please do not reply."

    for person, appt in make_reminder_list():
        if person.email_me == 1:
            # plug in the bits to create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email # TODO this has to be changed in production: receiver_email -> person.email
            message["Subject"] = subject
            # Add body to email
            body = f'Hi {person.first},\nYour appointment with Kellye is {str(appt)} {additional_text}'
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
                    server.sendmail(sender_email, receiver_email, message.as_string())
                    print(f'sent to {person.first}')
            except Exception as e:
                print(e)

