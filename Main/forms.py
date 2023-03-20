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
    submit = SubmitField("Continue")
    
    def validate_proteins(self, proteins):
        if not proteins.isnumeric():
            raise ValidationError('Enter Numbers')

    def validate_carbs(self, income_data: str):
        if not income_data.isnumeric():
            raise ValidationError('Enter Numbers')

    def validate_fats(self, income_data: str):
        if not income_data.isnumeric():
            raise ValidationError('Enter Numbers')