"Models module"

from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class CalculatorForm(FlaskForm):
    "Form for calculator page"
    proteins = IntegerField('Proteins',
                validators=[DataRequired()])
    carbs = IntegerField("Carbohydrates",
                validators=[DataRequired()])
    fats = IntegerField("Fats",
                validators=[DataRequired()])
    submit = SubmitField("Continue")
