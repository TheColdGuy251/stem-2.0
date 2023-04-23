from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class FriendsForm(FlaskForm):
    friend_id = IntegerField('ID друга', validators=[DataRequired()])
    submit = SubmitField('Отправить заявку')
