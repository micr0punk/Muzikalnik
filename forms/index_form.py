from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional

class SearchForm(FlaskForm):
    query = StringField('Поиск', validators=[Optional()])
    genre = SelectField('Жанр', choices=[
        ('', 'Все жанры'),
        ('rock', 'Рок'),
        ('pop', 'Поп'),
        ('hiphop', 'Хип-хоп'),
        ('jazz', 'Джаз'),
        ('electronic', 'Электронная музыка'),
    ])
    submit = SubmitField('Найти')
