from flask_wtf import FlaskForm
from wtforms  import Form, BooleanField, StringField, PasswordField, validators,TextAreaField

class RegisterForm(Form):
    firstName = StringField("First Name", [validators.DataRequired()])
    lastName = StringField("Last Name", [validators.DataRequired()])
    username = StringField('Username', [
        validators.Length(min=4, max=25),
        validators.DataRequired()
    ])
    email = StringField('Email Address', [
        validators.Length(min=6, max=35),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])

