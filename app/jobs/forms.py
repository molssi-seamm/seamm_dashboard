from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired

class EditJob(FlaskForm):
    name = StringField('Job Name', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Update Job')
