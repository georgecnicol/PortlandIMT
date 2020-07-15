from project import app
from project.core.twilio_send import twilio_contact
from project.core.gmail_send import send_mail
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    # can optionally remove next_run_time and will wait for 24 hours...
    scheduler.add_job(twilio_contact, 'interval', hours = 24, next_run_time = datetime.now())
    scheduler.add_job(send_mail, 'interval', hours = 24, next_run_time = datetime.now())
    scheduler.start()
    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()


