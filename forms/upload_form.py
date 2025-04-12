from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, DateField


class UploadAlbumForm(FlaskForm):
    name = StringField("Название альбома")
    artist = StringField("Исполнитель")
    genre = StringField("Жанр")
    length = StringField("Длительность")
    release_date = DateField("Дата релиза", format='%Y-%m-%d')
    cover = FileField("Обложка", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    submit = SubmitField("Загрузить альбом")


class UploadTrackForm(FlaskForm):
    name = StringField("Название трека")
    artist = StringField("Исполнитель")
    genre = StringField("Жанр")
    length = StringField("Длительность")
    release_date = DateField("Дата релиза", format='%Y-%m-%d')
    album_id = SelectField("Альбом (необязательно)", coerce=int, choices=[])
    cover = FileField("Обложка", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    submit = SubmitField("Загрузить трек")
