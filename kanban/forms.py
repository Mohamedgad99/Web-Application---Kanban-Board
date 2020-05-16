from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField
from kanban.models import User

class Tasks(FlaskForm):
	title = StringField('Title', validators=[
                           DataRequired(), Length(min=2, max=50)])
	description = TextAreaField('Description')
	deadline = DateField('Deadline', format='%Y-%m-%d', validators=[DataRequired()])
	submit = SubmitField('Add Task')


# User signup forms
class Signupform(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    passwordConfirm = PasswordField('Re-enter Password',
                                    validators=[DataRequired(), EqualTo('password')])
									#The validation for the confirmed password is that it matches the first input
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken, please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is used, please choose another one.')

#user login forms, where they can log into their accounts to see their kanban boards
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
