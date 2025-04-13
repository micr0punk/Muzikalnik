from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional
from data.genres import GENRES

class SearchForm(FlaskForm):
    query = StringField('Поиск', validators=[Optional()])
    genre = SelectField('Жанр', choices=[('', 'Все жанры')] + GENRES)
    submit = SubmitField('Найти')
