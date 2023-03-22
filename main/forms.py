"Models module"

import json
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectMultipleField, widgets
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
    
# class MealForm(SelectMultipleField):
#     "Form to choose meal"
#     meal = SelectMultipleField(label='test', validators=[DataRequired()])
#     submit = SubmitField('Submit')
    
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ExampleForm(FlaskForm):
    data = []
    with open('main/data/meals.json', "r", encoding='utf-8') as file:
        info = json.load(file)
        for meal in info['soups']:
            data.append(meal)
    choices = MultiCheckboxField('Routes', coerce=int, choices=data)
    submit = SubmitField("Set User Choices")