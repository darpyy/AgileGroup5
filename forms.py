from flask_wtf import FlaskForm
from wtforms import stringFiled, PasswordField, SubmitField, Booleanfiled
from wtforms.validators import DataRequired, Lenghth, Email, EqualTo

class RegistrationForm(FlaskForm):

    # a class that contains signup form and each object contains labels

    username = stringFiled('Username', validators=[DataRequired(), Lenghth(min=2, max=20)])
    email = stringFiled('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign_Up')

class loginForm(FlaskForm):

    # a class that contains login form and each object contains labels

    email = stringFiled('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = Booleanfiled('Remember Me')
    submit = SubmitField('Login')

