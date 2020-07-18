from project import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime as dt


# There are two kinds of appointments:
# available - an appointment held by the MC User (Master Calendar) that is available to HU (Human User)
# booked - an appointment that is held by a Human User
available = 'available'
booked = 'booked'
paid = 'paid'
due = 'due'


# compute for recurring appointments
def add_one_week(self, some_dt_date):
    one_week = dt.timedelta(days = 7)
    return some_dt_date + one_week


# allows us to do 'if user is authenticated' stuff
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    profile_image = db.Column(db.String(), nullable = False, default = 'default_image.png')
    email = db.Column(db.String(), unique = True, index = True)
    first = db.Column(db.String())
    last = db.Column(db.String(), index = True)
    password_hash = db.Column(db.String())
    phone = db.Column(db.String())

    # using int since sqlite doesnt have native bool and
    # is a PITA when you try t use it with forms.
    # looking for a 1 for admin... zero (or anything else is not)
    # but in the future higher numbers could allow for more privs
    is_admin = db.Column(db.Integer())
    email_me = db.Column(db.Integer())
    text_me = db.Column(db.Integer())

    # create a User.appointment attribute made from the Appointment model
    # and at the same time make a Appointment.user attribute ...
    # appointment = db.relationship('Appointment', backref='user' )

    # i prefer to make it locally though in each place separately:
    # which means you have to set up the attribute called 'user'
    # within Appointment and back populate it to User.appointment
    appointment = db.relationship('Appointment', back_populates = 'user')

    def __init__(self, email, first, last, password, phone, email_me, text_me):
        self.email = email
        self.first = first
        self.last = last
        self.password_hash = generate_password_hash(password)
        self.phone = phone
        self.is_admin = 0
        self.email_me = email_me
        self.text_me = text_me

    def __repr__(self):
        return f"{self.first} {self.last} ({self.email})"

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_new_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_admin(self, maybe):
        self.is_admin = maybe


class Appointment(db.Model):
    __tablename__ = 'appointments'
    status = db.Column(db.String(), index = True)
    #datetime style tuple of the form (year, month, day, hour, 30 or 00)
    start_time = db.Column(db.DateTime, primary_key = True, index = True)
    length = db.Column(db.Integer, index = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates = 'appointment')
    message = db.Column(db.String()) # special message from admin
    payment = db.Column(db.String()) # paid/ due

    # should be available only to admin or as part of admin suite
    def get_user(self):
        return f'{self.user.first} {self.user.last}'

    # create a new appointment and mark as available
    # length of appointment in minutes
    def __init__(self, start_time, length, message = ''):
        self.start_time = start_time # (YYYY, MM, DD, hh, mm, ss)
        self.length = length
        self.status = available
        self.message = message
        self.payment = due

    # need to make time readable for clients
    def __repr__(self):
        return  f'{self.start_time.strftime("%A, %B %d, %Y %I:%M %p")} for {self.length} minutes.'

    def show_time(self):
        return f'{self.start_time.strftime("%I:%M %p")} for {self.length} minutes'

    def toggle_payment(self):
        if self.payment == 'paid':
            self.payment = 'due'
        else:
            self.payment = 'paid'



    # put datetime into format matching calendar regex search so we can match an object to its calendar area
    # eg: wed">24<
    # does it make more sense to pass in the object and then return T/F on match?
    def match_cal(self):
        day = f'{self.start_time.strftime("%A")}'.lower()[0:3]+'">'+f'{self.start_time.strftime("%d")}'+'<'
        return day



