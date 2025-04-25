from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.fields.simple import HiddenField


class UploadAlbumForm(FlaskForm):
    form_name = HiddenField(default='album')
    name = StringField("Название альбома")
    artist = StringField("Исполнитель")
    genre = StringField("Жанр(ы) (Через запятую)")
    length = StringField("Длительность")
    release_date = DateField("Дата релиза", format='%Y-%m-%d')
    cover = FileField("Обложка", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    # audio_files = MultipleFileField("Треки альбома", validators=[
    #     FileAllowed(['mp3', 'wav', 'ogg', 'm4a'], 'Только аудиофайлы!')
    # ])
    submit = SubmitField("Загрузить альбом")


class UploadTrackForm(FlaskForm):
    form_name = HiddenField(default='track')
    name = StringField("Название трека")
    artist = StringField("Исполнитель")
    genre = StringField("Жанр(ы) (Через запятую)")
    length = StringField("Длительность")
    release_date = DateField("Дата релиза", format='%Y-%m-%d')
    album_id = SelectField("Альбом (необязательно)", coerce=int, choices=[])
    cover = FileField("Обложка", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    audio_file = FileField("Аудиофайл", validators=[
        FileAllowed(['mp3', 'wav', 'ogg', 'm4a'], 'Только аудиофайлы!')
    ])
    submit = SubmitField("Загрузить трек")
