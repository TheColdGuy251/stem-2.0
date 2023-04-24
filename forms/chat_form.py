from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Отправить')