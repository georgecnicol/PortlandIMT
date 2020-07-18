# users/forms
import wtforms
from flask_wtf import FlaskForm, RecaptchaField
from project.models import User
from flask_login import current_user


# holds the submit button
class SubmitForm(FlaskForm):
    submit = wtforms.SubmitField('Submit')


class BasicEmail(SubmitForm):
    email = wtforms.StringField('Email', validators = [wtforms.validators.InputRequired(), wtforms.validators.Email()])

    # look in the db to ensure email is not there already
    # TRUE indicates unique email
    def check_email_unique(self, email):
        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user is None or user.email == current_user.email:
            return True
        return False


class UpdateEmailForm(BasicEmail):
    email_me = wtforms.SelectField('Text', coerce = int,
                                   choices = [(1, 'Please send appointment reminder email'),
                                              (0, 'Do not send appointment reminder email')])


class AlterAdminForm(BasicEmail):
    add_or_remove = wtforms.RadioField('Admin?', coerce = int, choices = [(1, 'Add'), (0, 'Remove')])


class LoginForm(BasicEmail):
    password = wtforms.PasswordField('Password', validators = [wtforms.validators.InputRequired()])
    recaptcha = RecaptchaField()


class RegisterForm(LoginForm):
    first = wtforms.StringField('First Name', validators = [wtforms.validators.InputRequired()])
    last = wtforms.StringField('Last Name', validators = [wtforms.validators.InputRequired()])
    pass_confirm = wtforms.PasswordField('Confirm Password',
                                         validators = [wtforms.validators.InputRequired(),
                                                       wtforms.validators.EqualTo('password')])
    area = wtforms.StringField('Area Code',
                               validators = [wtforms.validators.InputRequired(),
                                             wtforms.validators.Regexp('^\d+$'),
                                             wtforms.validators.Length(min = 3, max = 3)])
    exchange = wtforms.StringField('Phone Number',
                                   validators = [wtforms.validators.InputRequired(),
                                                 wtforms.validators.Regexp('^\d+$'),
                                                 wtforms.validators.Length(min = 3, max = 3)])
    subscriber = wtforms.StringField('',
                                     validators = [wtforms.validators.InputRequired(),
                                                   wtforms.validators.Regexp('^\d+$'),
                                                   wtforms.validators.Length(min = 4, max = 4)])

    email_me = wtforms.SelectField('Email me', coerce = int,
                                   choices = [(1, 'Please send appointment reminder email'),
                                              (0, 'Do not send appointment reminder email')])

    text_me = wtforms.SelectField('Text me', coerce = int,
                                  choices = [(1, 'Please send appointment reminder text'),
                                             (0, 'Do not send appointment reminder text')])

    token = wtforms.StringField('',
                                validators = [wtforms.validators.InputRequired()])


class UpdatePhoneForm(SubmitForm):
    area = wtforms.StringField('Area Code',
                               validators = [wtforms.validators.InputRequired(),
                                             wtforms.validators.Regexp('^\d+$'),
                                             wtforms.validators.Length(min = 3, max = 3)])
    exchange = wtforms.StringField('Phone Number',
                                   validators = [wtforms.validators.InputRequired(),
                                                 wtforms.validators.Regexp('^\d+$'),
                                                 wtforms.validators.Length(min = 3, max = 3)])
    subscriber = wtforms.StringField('',
                                     validators = [wtforms.validators.InputRequired(),
                                                   wtforms.validators.Regexp('^\d+$'),
                                                   wtforms.validators.Length(min = 4, max = 4)])

    text_me = wtforms.SelectField('Text', coerce = int,
                                  choices = [(1, 'Please send appointment reminder texts'),
                                             (0, 'Do not send appointment reminder texts')])


class UpdatePasswordForm(SubmitForm):
    old_password = wtforms.PasswordField('Old Password', validators = [wtforms.validators.InputRequired()])
    new_password = wtforms.PasswordField('New Password', validators = [wtforms.validators.InputRequired()])
    confirm_pass = wtforms.PasswordField('Confirm Password',
                                         validators = [wtforms.validators.InputRequired(),
                                                       wtforms.validators.EqualTo('new_password')])
