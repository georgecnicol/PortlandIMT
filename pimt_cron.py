# runs as cron job
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from project import get_config
from project.core.gmail_send import send_mail
from project.core.twilio_send import twilio_contact

config = get_config()
today = datetime.now()
tomorrow = today + relativedelta(hours = 24)
cut_off = tomorrow + relativedelta(hours = 24)
tomorrow = tomorrow.strftime('%Y-%m-%d')
cut_off = cut_off.strftime('%Y-%m-%d')


conn = sqlite3.connect('/home/ubuntu/PIMT/project/data.sqlite')

c = conn.cursor()
c.execute('SELECT * FROM appointments WHERE start_time >= ? AND start_time < ? AND status = "booked"', (tomorrow, cut_off))
appts = c.fetchall()
users = []
for appt in appts:
    c.execute('SELECT * FROM users WHERE id = ?', (appt[2],))
    users.append(c.fetchone())

conn.close()

for u,a in zip(users, appts):
    a = datetime.strptime(a[1][:19], '%Y-%m-%d %H:%M:%S')
    a = a.strftime("%A, %B %d, %Y %I:%M %p")
    if u[8] == 1:  #email
        send_mail(config, u[3], a, u[2])
    if u[9] == 1:  #text
        twilio_contact(config, u[3], a, u[7])

# (7, 'default_image.png', 'foo@bar.com', 'First', 'Last', b'$2b$12tY0oM5ghCunaQ/lb/XeyVse3T8y', 0, '123567890', 1, 1)