"Models module"

import json
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectMultipleField, widgets, \
            StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, Length


class CalculatorForm(FlaskForm):
    "Form for calculator page"
    proteins = IntegerField('Proteins',
                validators=[DataRequired()])
    carbs = IntegerField("Carbohydrates",
                validators=[DataRequired()])
    fats = IntegerField("Fats",
                validators=[DataRequired()])
    submit = SubmitField("Continue")

class MultiCheckboxField(SelectMultipleField):
    "Multi check box field"
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ExampleForm(FlaskForm):
    "Example form"
    data = []
    with open('main/data/meals.json', "r", encoding='utf-8') as file:
        info = json.load(file)
        for meal_category in info:
            for meal in info[meal_category]:
                data.append(meal)
    choices = MultiCheckboxField('Available dishes', choices=sorted(data))
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    "Login form"
    email = StringField("Email",
                    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Agree to terms', validators=[DataRequired()])
    submit = SubmitField("Login")

class RegistrationForm(FlaskForm):
    "Registration Form"
    username = StringField('Username',
                    validators=[DataRequired(), Length(min=2, max = 20)])
    email = StringField("Email",
                    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")
