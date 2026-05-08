from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):

    # a class that contains signup form and each object contains labels

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign_Up')

class loginForm(FlaskForm):

    # a class that contains login form and each object contains labels

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# a class form for the posts

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    body  = TextAreaField('Body',  validators=[DataRequired()])
    submit = SubmitField('Post')


# a class form for creating requests

class RequestForm(FlaskForm):

    reqtitle = StringField('Title', validators=[DataRequired(), Length(min=2, max=20)])
    reqdescription = StringField('Description', validators=[DataRequired(), Length(min=5, max=100)])
    submit = SubmitField('Request')

    # a class form for creating activities

class ActivityForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=20)])
    description = StringField('Description', validators=[DataRequired(), Length(min=5, max=100)])
    submit = SubmitField('Create')