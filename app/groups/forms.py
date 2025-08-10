from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class CreateGroupForm(FlaskForm):
    """Form for creating a new Susu group"""
    name = StringField('Group Name', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    description = TextAreaField('Description')
    cycle_size = IntegerField('Number of Members', validators=[
        DataRequired(),
        NumberRange(min=2, max=50, message='Group size must be between 2 and 50 members')
    ])
    weekly_amount = DecimalField('Weekly Contribution Amount (₵)', validators=[
        DataRequired(),
        NumberRange(min=1, message='Amount must be greater than 0')
    ])
    submit = SubmitField('Create Group')