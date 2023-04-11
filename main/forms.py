"Models module"

import re
from flask_wtf import FlaskForm, file
from PIL import Image, UnidentifiedImageError
from flask_login import current_user
from wtforms import SubmitField, IntegerField, SelectMultipleField, widgets, \
    StringField, PasswordField, BooleanField, SelectField, RadioField, FileField,\
        FieldList, FormField, SearchField
from wtforms.validators import DataRequired, EqualTo, Email, \
    Length, NumberRange, ValidationError
from main.models import User, Meal

class CalculatorForm(FlaskForm):
    "Form for calculator page"
    proteins = IntegerField('Proteins (g)',
                validators=[DataRequired(), NumberRange(min=0)])
    carbs = IntegerField("Carbohydrates (g)",
                validators=[DataRequired(), NumberRange(min=0)])
    fats = IntegerField("Fats (g)",
                validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Continue")

class MultiCheckboxField(SelectMultipleField):
    "Multi check box field"
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.CheckboxInput()

class MultiCheckboxFormMeals(FlaskForm):
    "MultiCheckBox Form"
    choices = MultiCheckboxField('', choices=[])

class MultiCheckboxFormSettings(FlaskForm):
    "MultiCheckBox Form"
    choices = MultiCheckboxField('', choices=[], coerce=str)


class MealForm(FlaskForm):
    "Meal Form"
    search = SearchField()
    meals = FieldList(FormField(MultiCheckboxField))
    submit = SubmitField("Submit")

class SettingsForm(FlaskForm):
    'Settings Form'
    unrepeatable = MultiCheckboxField('Unrepeatable meals', choices=[], coerce=str)
    portions = FieldList(FormField(MultiCheckboxField))
    option = SelectField('Options to show', choices = [(x, x) for x in range(1, 21)], coerce=int)
    amount = SelectField('Max amount of dishes in meal',
        choices=[(x, x) for x in range(1, 7)], coerce=int)
    submit = SubmitField("Save")

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
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=100)])
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

    def validate_password(self, password):
        'Password validation'
        res_1 = re.findall('[A-z]', password.data)
        if not res_1:
            raise ValidationError('Password must contain letters')
        res_2 = re.findall(r'\d', password.data)
        if not res_2:
            raise ValidationError('Password must contain numbers')

class PersonalInfoForm(FlaskForm):
    "Personal Info form"
    sex = SelectField('Sex', choices=['Male', 'Female'],
        validate_choice=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=16, max=120)])
    height = IntegerField('Height (cm)', validators=[DataRequired(), NumberRange(min=120, max=250)])
    weight = IntegerField('Weight (kg)', validators=[DataRequired(), NumberRange(min=1, max=700)])
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
    proteins = IntegerField('Proteins (g)',
                validators=[DataRequired(), NumberRange(min=0)])
    carbs = IntegerField("Carbohydrates (g)",
                validators=[DataRequired(), NumberRange(min=0)])
    fats = IntegerField("Fats (g)",
                validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Add Meal")

    def validate_meal_name(self, meal_name):
        'Validates meal name'
        meal = Meal.query.filter_by(name = meal_name.data, user_id = current_user.id).first()
        if meal:
            raise ValidationError('Meal with such name already exists, please choose another one')

class PossibleMeals(FlaskForm):
    "Possible Meals form"
    dish_var = RadioField('Choose one from the list:',
            choices=[], validate_choice=[DataRequired()], coerce=int)
    submit = SubmitField("Submit")

class UpdateAccountForm(FlaskForm):
    "Update user info Form"
    username = StringField('Username',
                    validators=[DataRequired(), Length(min=2, max = 20)])
    sex = SelectField('Sex', choices=['Male', 'Female'],
        validate_choice=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=16, max=120)])
    height = IntegerField('Height (cm)', validators=[DataRequired(), NumberRange(min=120, max=250)])
    weight = IntegerField('Weight (kg)', validators=[DataRequired(), NumberRange(min=1, max=700)])
    goal = SelectField('Goal', choices=[(2, 'Gain'),(3, 'Maintain'), (1, 'Loose')],
        validate_choice=[DataRequired()], coerce=int)
    activity = SelectField('Activity', choices=[(1.2, 'Passive lifestyle'),
    (1.4, 'Active lifestyle with 2-3 workouts a week'),
    (1.46, 'Active lifestyle with 4-5 workouts a week'),
    (1.55, 'Active lifestyle with 5-6 workouts a week'),
    (1.8, 'Active lifestyle with more than 6 workouts a week')], coerce=float)
    servings = SelectField('Servings', choices = [], coerce=int)
    submit = SubmitField("Update")
    picture = FileField('Update Profile Picture',
            validators=[file.FileAllowed(['jpg', 'png', 'jpeg'])])

    def validate_username(self, username: str) -> None:
        "Validates username"
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose different one')

    def validate_picture(self, picture) -> None:
        "Validates picture"
        if picture.data.filename != '':
            try:
                Image.open(picture.data)
            except UnidentifiedImageError as exc:
                raise ValidationError("Imported file seems to be corrupted") from exc

class CustomPlan(FlaskForm):
    'Custom Plan class'
    plan_choice = RadioField("Choose Plan",
        choices=[(0, "Use auto-generated"), (1, "Mannual")],
        validate_choice=[DataRequired()], coerce=int)
    submit = SubmitField("Update")

class PersonalPlan(FlaskForm):
    'Personal Plan class'
    proteins = IntegerField('Proteins (g)',
                validators=[DataRequired(), NumberRange(min=0)])
    carbs = IntegerField("Carbohydrates (g)",
                validators=[DataRequired(), NumberRange(min=0)])
    fats = IntegerField("Fats (g)",
                validators=[DataRequired(), NumberRange(min=0)])

class RequestResetForm(FlaskForm):
    'Request reset form'
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        'Validates email'
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    'Reset Password Form'
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
