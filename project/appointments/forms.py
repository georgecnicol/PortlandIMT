import wtforms
from flask_wtf import FlaskForm


# holds the submit button
class SubmitForm(FlaskForm):
    submit = wtforms.SubmitField('Submit')


class CreateAppt(SubmitForm):
    YYYY = wtforms.SelectField('Year', coerce = int,
                               choices = [(2020, '2020'), (2021, '2021'), (2022, '2022')])

    MM = wtforms.SelectField('Month', coerce = int,
                             choices = [(1, 'Jan'), (2, 'Feb'), (3, 'Mar'),
                                        (4, 'Apr'), (5, 'May'), (6, 'June'),
                                        (7, 'Jul'), (8, 'Aug'), (9, 'Sep'),
                                        (10, 'Oct'), (11, 'Nov'), (12, 'Dec')])

    # validation for actual appropriate day for the month in question is handled by
    # try/except block associated with datatime creation
    DD = wtforms.IntegerField('Date', validators = [wtforms.validators.InputRequired()])

    type = wtforms.SelectField('Type of Appointment',
                               choices = [('single', 'single'),
                                          ('type_a', '7 hour: 2 x 90 min and 2 x 2hr'),
                                          ('type_b', '6 hour: 4 x 90 min'),
                                          ('type_c', '5 hour: 1 x 2hr and 2 x 90 min')])

    hh = wtforms.SelectField('Hour', coerce = int, choices = [(9, '9AM'), (10, '10AM'), (11, '11AM'),
                                                              (12, 'Noon'), (13, '1PM'), (14, '2PM'),
                                                              (15, '3PM'), (16, '4PM'), (17, '5PM')])

    mm = wtforms.SelectField('Minutes', coerce = int, choices = [(0, ':00'), (30, ':30')])

    length = wtforms.SelectField('Length of Appointment', coerce = int,
                                 choices = [(60, '60 minutes'), (90, '90 minutes'), (120, '120 minutes')])

    # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans
    create = wtforms.SelectField('Create or Delete Appointment', coerce = (lambda x: x == 'True'), choices = [(True, 'create'), (False, 'delete')])

    message = wtforms.StringField('Optional Short Message Displayed at Time of Booking',
                                  validators = [wtforms.validators.Optional()])


