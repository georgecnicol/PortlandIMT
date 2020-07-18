# besides making a single appointment for some set amount of time
# there are several appointment patterns
# a) 9-1030, 1030-12, 1-3, 3-5 (2 x 90min + 2 x 2 hr) which is 7 hours
# b) 9-1030, 1030-12, 1-230, 230-4 (4 x 90min) which is 6 hours
# c) 9-11, 12-130, 130-3 (1 x 2hr + 2 x 90min) which is 5 hours
# ideally a work week is two type (a) days and one type (b) day for 20 hours.
from project.models import Appointment, User
from project import db
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from flask_login import current_user
from sqlalchemy import and_
from flask import flash



offset_start = timedelta(hours = 9)
offset_90 = timedelta(hours = 1, minutes = 30)
offset_lunch = timedelta(hours = 1)
offset_120 = timedelta(hours = 2)
type_a = [(offset_start, 90), (offset_90, 90), ((offset_90 + offset_lunch), 120), (offset_120, 120)]
type_b = [(offset_start, 90), (offset_90, 90), ((offset_90 + offset_lunch), 90), (offset_90, 90)]
type_c = [(offset_start, 120), ((offset_120 + offset_lunch), 90), (offset_90, 90)]
day_type = {'type_a': type_a, 'type_b': type_b, 'type_c': type_c}


#
def update_payment(dt_obj, payment):
    appt = Appointment.query.filter_by(start_time = dt_obj).first()
    if appt is not None:
        appt.payment = payment
        db.session.commit()


# length of appointment in minutes
def create_single(dt_obj, length, create, message = ''):
    if create:
        appointment_end = dt_obj + relativedelta(minutes = length)
        if len(Appointment.query.filter(and_(Appointment.start_time >= dt_obj, Appointment.start_time < appointment_end)).all()) == 0:
            db.session.add(Appointment(dt_obj, length, message))
            flash(f'Appointment created on {dt_obj.strftime("%A, %B %d, %Y %I:%M %p")}.')
        else:
            flash(f'There is already an appointment on {dt_obj.strftime("%A, %B %d, %Y %I:%M %p")}.')
    else:
        appt = Appointment.query.filter_by(start_time = dt_obj).first()
        if appt is not None:
            db.session.delete(appt)
            flash(f'Appointment on {dt_obj.strftime("%A, %B %d, %Y %I:%M %p")} deleted.')
        else:
            flash(f'No appointment found on {dt_obj.strftime("%A, %B %d, %Y %I:%M %p")}.')

    db.session.commit()


# dt_obj needs to be date of format YYYY, MM, DD, 00, 00, 00
def create_day(dt_obj, list_type, create):
    for offset, length in list_type:
        dt_obj = dt_obj + offset
        create_single(dt_obj, length, create)


# determine if we are booking or canceling an appointment
# based on part of the link passed in
def make_or_cancel(month_year):
    action = month_year.split('_')[1]
    if action == 'b':
        action = 'book'
    else:
        action = 'cancel'

    return action


# receives a month_year format that should be 24 H but isn't because
# it is coming from a AM/PM time
# any appointment that has an hour as 4, really means 4PM .. or 4+12
# returns:
# - a text style date used in a flash message
# - a dt_obj used in db query
# - boolean indicating if we are violating 24 hour window
# while these are all used in different places, they are all generated from the same
# bit of information passed in.
def translator_for(month_year):
    month_year = month_year.split('_')[0]
    dt_obj = datetime.strptime(month_year, '%Y-%m-%d-%H-%M')
    if dt_obj.hour < 7:
        dt_obj = dt_obj + relativedelta(hours = 12)
    date = dt_obj.strftime('%A, %B %d, %Y %I:%M %p') # this goes in render template
    cancel_time_limit = datetime.today() + relativedelta(hours = 24)
    return date, dt_obj, dt_obj < cancel_time_limit


# returns zipped user and ALL booked appointment list (current or past appts) or None
# and the users who have those appointments
# for admin consumption only
def admin_list_booked(dt_obj):
    current_users = []
    past_users = []
    current = []
    past = []
    if current_user.is_admin:
        current = Appointment.query.filter(and_(
            Appointment.status == 'booked', Appointment.start_time > dt_obj)).order_by(
            Appointment.start_time).all()
        past = Appointment.query.filter(and_(
            Appointment.status == 'booked', Appointment.start_time <= dt_obj)).order_by(
            Appointment.start_time.desc()).all()
        for appt in current:
            current_users.append(db.session.query(User).get(appt.user_id))
        for appt in past:
            past_users.append(db.session.query(User).get(appt.user_id))

    return zip(current_users, current), zip(past_users, past)


# return a tuple consiting of two lists of appointments associated with a user
# one list is for appointments that have yet to occur, the other for appointments
# that have already occurred
def list_appts(dt_obj, user_id):
    current = db.session.query(Appointment).filter(
        and_(Appointment.user_id == user_id, Appointment.status == 'booked',
             Appointment.start_time > dt_obj)).order_by(Appointment.start_time)
    past = db.session.query(Appointment).filter(
        and_(Appointment.user_id == user_id, Appointment.status == 'booked',
             Appointment.start_time <= dt_obj)).order_by(Appointment.start_time.desc())

    return current, past


# return a list appointments that have a status of available; 25 maximum
def list_available(dt_obj):
    avail = Appointment.query.filter_by(status = 'available').filter(
        Appointment.start_time >= dt_obj).order_by(Appointment.start_time).limit(25)
    return avail


# get a list of booked appointments that are
# FROM the time passed in TO a time 24 hours ahead of that
def get_one_day_of_booked(dt_obj):
    booked = db.session.query(Appointment).filter(and_(
        Appointment.status == 'booked',
        Appointment.start_time >= dt_obj,
        Appointment.start_time <= dt_obj+relativedelta(hours = 24))).all()

    return booked


# get the users associated with the appointments passed in - which are presumably 'booked'
def get_users(list_of_appointments):
    users = []
    for appt in list_of_appointments:
        users.append(User.query.filter_by(id = appt.user_id).first())

    return users


# we want to make a list of appointments, for which to send out reminders
# that list consists of all booked appointments that start between
# 24 and 48 hours from when the list is created.
def make_reminder_list():
    # figure out the day and when to look for appointments
    today = datetime.today()
    tomorrow = today + relativedelta(days = 1)
    booked = get_one_day_of_booked(tomorrow)
    users = get_users(booked)

    return zip(users, booked)


# the toggle button in list, within appointments view, passes a datetime string
# to the href view it calls. We need that string converted back to a dt object
# so we can use it to access the associated appointment in the database
def make_dt(dt_string):
    return datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')

