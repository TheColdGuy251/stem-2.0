from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class AddGamesForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    link = StringField('Ссылка на загрузку', validators=[DataRequired()])
    submit = SubmitField("Добавить")