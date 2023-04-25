from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, HiddenField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    image = FileField(validators=[
        FileAllowed(['jpg', 'png'], 'The file format should be .jpg or .png.')
    ])
    submit_image = SubmitField('Показать')
