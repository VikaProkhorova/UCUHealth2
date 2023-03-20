from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError 


class CalculatorForm(FlaskForm):
    proteins = StringField('Proteins',
                validators=[DataRequired()])
    carbs = StringField("Carbohydrates", 
                validators=[DataRequired()])
    fats = StringField("Fats", 
                validators=[DataRequired()])

