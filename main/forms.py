"Models module"

import json
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField, IntegerField, SelectMultipleField, widgets, \
            StringField, PasswordField, BooleanField, SelectField, RadioField
from wtforms.validators import DataRequired, EqualTo, Email, \
            Length, NumberRange, ValidationError
from main.models import User

class CalculatorForm(FlaskForm):
    "Form for calculator page"
    proteins = IntegerField('Proteins',
                validators=[DataRequired(), NumberRange(min=0)])
    carbs = IntegerField("Carbohydrates",
                validators=[DataRequired(), NumberRange(min=0)])
    fats = IntegerField("Fats",
                validators=[DataRequired(), NumberRange(min=0)])
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
    remember = BooleanField('Remember me')
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
    submit = SubmitField("Continue")

    def validate_username(self, username: str) -> None:
        "Validates username"
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose different one')

    def validate_email(self, email: str) -> None:
        "Validates email"
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose different one')

class PersonalInfoForm(FlaskForm):
    "Personal Info form"
    sex = SelectField('Sex', choices=['Male', 'Female'],
        validate_choice=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=16, max=120)])
    height = IntegerField('Height', validators=[DataRequired(), NumberRange(min=120, max=250)])
    weight = IntegerField('Weight', validators=[DataRequired(), NumberRange(min=1, max=700)])
    goal = SelectField('Goal', choices=[(2, 'Gain'),(3, 'Maintain'), (1, 'Loose')],
        validate_choice=[DataRequired()], coerce=int)
    agree = BooleanField('Agree to the processing of my data',
        validators=[DataRequired()])
    activity = SelectField('Activity', choices=[(1.2, 'Passive lifestyle'),
    (1.4, 'Active lifestyle with 2-3 workouts a week'),
    (1.46, 'Active lifestyle with 4-5 workouts a week'),
    (1.55, 'Active lifestyle with 5-6 workouts a week'),
    (1.8, 'Active lifestyle with more than 6 workouts a week')],
        validate_choice=[DataRequired()], coerce=float)
    submit = SubmitField("Submit")

class AddMeal(FlaskForm):
    "Adds meal to user"
    meal_name = StringField('Meal name', validators=[DataRequired()])
    proteins = IntegerField('Proteins',
                validators=[DataRequired(), NumberRange(min=0)])
    carbs = IntegerField("Carbohydrates",
                validators=[DataRequired(), NumberRange(min=0)])
    fats = IntegerField("Fats",
                validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Add Meal")

class PossibleMeals(FlaskForm):
    "Possible Meals form"
    dish_var = RadioField('Choose one from the list:',
            choices=[], validate_choice=[DataRequired()])
    submit = SubmitField("Submit")

class UpdateAccountForm(FlaskForm):
    "Update user info Form"
    username = StringField('Username',
                    validators=[DataRequired(), Length(min=2, max = 20)])
    email = StringField("Email",
                    validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    sex = SelectField('Sex', choices=['Male', 'Female'],
        validate_choice=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=16, max=120)])
    height = IntegerField('Height', validators=[DataRequired(), NumberRange(min=120, max=250)])
    weight = IntegerField('Weight', validators=[DataRequired(), NumberRange(min=1, max=700)])
    goal = SelectField('Goal', choices=[(2, 'Gain'),(3, 'Maintain'), (1, 'Loose')],
        validate_choice=[DataRequired()], coerce=int)
    activity = SelectField('Activity', choices=[(1.2, 'Passive lifestyle'),
    (1.4, 'Active lifestyle with 2-3 workouts a week'),
    (1.46, 'Active lifestyle with 4-5 workouts a week'),
    (1.55, 'Active lifestyle with 5-6 workouts a week'),
    (1.8, 'Active lifestyle with more than 6 workouts a week')], coerce=float)
    submit = SubmitField("Update")

    def validate_username(self, username: str) -> None:
        "Validates username"
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose different one')

    def validate_email(self, email: str) -> None:
        "Validates email"
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose different one')

class CustomPlan(FlaskForm):
    'Custom Plan class'
    plan_choice = RadioField("Choose Plan",
        choices=[(False, "Use auto-generated"), (True, "Mannual")],
        validate_choice=[DataRequired()], coerce=bool)
    submit = SubmitField("Update")
