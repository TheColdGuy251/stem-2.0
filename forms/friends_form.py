from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class FriendsForm(FlaskForm):
    friend_id = TextAreaField('Друзья', validators=[DataRequired()])
    submit = SubmitField('Добавить В Друзья')