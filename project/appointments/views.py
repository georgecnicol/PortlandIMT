from project import db
from flask import render_template, redirect, url_for, Blueprint, flash
from flask_login import current_user, login_required
from project.models import Appointment
from project.appointments.forms import CreateAppt, SubmitForm
import project.appointments.apt_creator as creator
import project.appointments.calendar as cal
from datetime import datetime, timedelta


appointments = Blueprint('appointments', __name__, template_folder = 'templates/appointments')


@appointments.route('/list')
@login_required
def list_appointments():
    dt_obj = datetime.today()
    # all available appts
    avail = creator.list_available(dt_obj)
    # admins get to see all appointments booked by everyone as well as all available
    now_booked, past_booked = creator.admin_list_booked(dt_obj)
    # users get to see their own appointments and available appointments
    now_user, past_user = creator.list_appts(dt_obj, current_user.id)

    return render_template('list-appointments.html', now_booked = now_booked, past_booked = past_booked,
                           avail = avail, now_user = now_user, past_user = past_user)


# create an appointment. can be a specific appointment or a set of appointments
# via a form
@appointments.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    form = CreateAppt()
    if form.validate_on_submit():
        try:
            day = datetime(form.YYYY.data, form.MM.data, form.DD.data)
        except ValueError:
            flash('That month does not have that many days.')
            return redirect(url_for('appointments.create'))

        schedule = form.type.data
        if 'single' not in schedule: # create a batch of appointments
            creator.create_day(day, creator.day_type[schedule], form.create.data)
        else:
            day = day + timedelta(hours = form.hh.data, minutes = form.mm.data)
            creator.create_single(day, form.length.data, form.create.data, form.message.data)
        return redirect(url_for('appointments.create'))
    return render_template('create.html', form = form)


# calendar month and year display -or- confirm to book/cancel appt
@appointments.route('/<month_year>', methods = ['GET', 'POST'])
@login_required
def view_sometime(month_year):
    # calendar display
    next_month, last_month = cal.some_calendar(month_year)
    if next_month is not None:
        return render_template('calendar.html', current_calendar = cal.make_html_calendar(month_year),
                               next_month = next_month, last_month = last_month)

    # client is booking/ cancelling an appointment
    # incoming format is YYYY-MM-DD-hh-mm-stuff
    form = SubmitForm()
    action = creator.make_or_cancel(month_year)
    date, start_time, invalid_time = creator.translator_for(month_year)

    if form.validate_on_submit():
        if invalid_time:
            flash(f'Sorry, you cannot book or cancel appointments less than 24 hours in advance.')
        else:
            appt = Appointment.query.filter_by(start_time = start_time).first()
            if appt.status == 'available':
                appt.status = 'booked'
                appt.user_id = current_user.id
                flash(f'You booked {appt}')
            else:
                appt.status = 'available'
                flash(f'You cancelled {appt}')
            db.session.commit()

        return redirect(url_for('appointments.calendar'))

    appt = Appointment.query.filter_by(start_time = start_time).first()
    if appt.message is not None and not appt.message == '':
        flash(appt.message)
    return render_template('confirm.html', form = form, date = date, action = action)


# this route is really only reached from the menu bar
# after that, successive calendar views will generally be from
# the month_year route via next/last buttons
@appointments.route('/calendar', methods = ['GET', 'POST'])
@login_required
def calendar():
    today = datetime.today()
    next_month, last_month = cal.next_and_last(today)
    today = today.strftime('%B') + '-' + today.strftime('%Y')
    # view_sometime(today)

    return render_template('calendar.html', current_calendar = cal.make_html_calendar(today),
                           next_month = next_month, last_month = last_month)


