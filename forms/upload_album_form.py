from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired

class UploadAlbumForm(FlaskForm):
    title = StringField("Название альбома")
    artist = StringField("Исполнитель")
    cover = FileField("Обложка", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    submit = SubmitField("Загрузить")
