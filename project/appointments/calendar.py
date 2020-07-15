from datetime import datetime, timedelta
from project.models import Appointment
import calendar
import re
from dateutil.relativedelta import relativedelta
from flask_login import current_user
from sqlalchemy import or_, and_


months_of_year = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                  'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11,
                  'december': 12}

# make a button group for a given calendar day
# we want the status also because that will determine display color
# depending on who is viewing the calendar
# TODO does empty query return list of length zero or None?
def get_appts_for_day(dt_obj, is_admin):
    delta = timedelta(hours = 24)
    dt_obj2 = dt_obj + delta
    if is_admin:
        avail = Appointment.query.filter(Appointment.start_time > dt_obj).filter(
            Appointment.start_time < dt_obj2).all()  # we want an empty list, not None
    else:
        # we have to include 'booked' with a user.id because a user can relinquish an
        # appointment to 'available' but it still stays attached to the user.id
        avail = Appointment.query.filter(Appointment.start_time > dt_obj).filter(
            Appointment.start_time < dt_obj2).filter(
            or_(Appointment.status == 'available',
                and_(Appointment.user_id == current_user.id,
                     Appointment.status == 'booked'))).order_by(Appointment.start_time).all()
        # button_list.append((appt.show_time(), appt.status))

    return avail


# creates the html select field for injection into calendar day
# creates the unique link for making/ cancelling appt
def button_avail(appt_time, dt_obj):
    # eg: YYYY-MM-DD-hh-mm ... 2020-09-02-01-30
    appt_2_edit = str(dt_obj.date()) + '-' + appt_time.split()[0].replace(':', '-') + '_b'
    html_start = f'<div class="dropdown"><button class="btn btn-outline-light dropdown-toggle form-control" type="button" id="avail" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">{appt_time}</button>'
    html_end =f'<div class="dropdown-menu bg-info" aria-labelledby="dropdownMenuButton"><a class="dropdown-item bg-info form-control" id="dropdown-text" href="{appt_2_edit}">book this time</a></div></div>'
    return html_start + html_end


# creates the html select field for injection into HTML calendar day
# creates the unique link for making/ cancelling appt
def button_booked(appt_time, dt_obj):
    # eg: YYYY-MM-DD-hh-mm ... 2020-09-02-01-30
    app_2_edit = str(dt_obj.date()) + '-' + appt_time.split()[0].replace(':', '-') + '_c'
    html_start = f'<div class="dropdown"><button class="btn btn-outline-light dropdown-toggle form-control" type="button" id="booked" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">{appt_time}</button>'
    html_end = f'<div class="dropdown-menu bg-info" aria-labelledby="dropdownMenuButton"><a class="dropdown-item  bg-info form-control" id="dropdown-text" href="{app_2_edit}">cancel this time</a></div></div>'
    return html_start + html_end


# match represents that calendar day in HTML calendar day, dt_obj is
# the datetime used under the hood to fetch appointments
# and the year is for text processing/ formatting
def assemble_buttons(match, dt_obj, year):
    first_part = match.group()[:-1] + ' '
    fields = ''
    for appt in get_appts_for_day(dt_obj, current_user.is_admin):
        if appt.status == 'available':
            fields += button_avail(str(appt).split(str(year))[1][1:], dt_obj)
        else:
            fields += button_booked(str(appt).split(str(year))[1][1:], dt_obj)
    return first_part + fields + '</div><'


# used in @appointments.route('/<month_year>')
# makes and formats the html calendar with buttons
def make_html_calendar(month_year):
    # make the requested calendar month
    month = months_of_year[month_year.split('-')[0].lower()]
    year = int(month_year.split('-')[1])
    html_cal = calendar.HTMLCalendar()

    # preliminary formatting on html for calendar
    current_calendar = html_cal.formatmonth(year, month, withyear = True)
    current_calendar = current_calendar.replace('spacing="0" class="month"', 'spacing="0" class="whole-month"')
    current_calendar = current_calendar.replace('cellpadding="0"', 'cellpadding="5"')
    current_calendar = current_calendar.replace('border="0"', 'border="1"')

    # use regex to find the occurrences of 'date' in html calendar
    # so that we can insert buttons on those days where there are appointments
    # in the database
    # there is a fair amount of specific formatting for the calendar
    for day, _ in enumerate(range(calendar.monthrange(year, month)[1]), 1):
        dt_obj = datetime(year, month, day)
        match = re.search(f'>{day}<', current_calendar)
        assembled_buttons = assemble_buttons(match, dt_obj, year)
        current_calendar = current_calendar.replace(match.group(), assembled_buttons)
    return current_calendar


# pre-formatting for next and last month buttons on calendar
def some_calendar(month_year):
    # might not be the right format
    try:
        month = months_of_year[month_year.split('-')[0].lower()]
        year = int(month_year.split('-')[1])
        sometime = datetime(year, month, 15)
        return next_and_last(sometime)
    except KeyError:
        return None, None


# make the next and last month buttons on calendar
def next_and_last(dt_obj):
    next_month = dt_obj + relativedelta(months = +1)
    last_month = dt_obj + relativedelta(months = -1)
    next_month = next_month.strftime('%B') + '-' + next_month.strftime('%Y')
    last_month = last_month.strftime('%B') + '-' + last_month.strftime('%Y')

    return next_month, last_month
