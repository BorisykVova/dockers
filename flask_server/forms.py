from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class InputForm(FlaskForm):
    key = StringField('Key', validators=[Required()])
    value = StringField('Value', validators=[Required()])
    submit = SubmitField('Submit')
