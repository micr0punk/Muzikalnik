import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Track(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'albums'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    artist = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    cover_url = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='/static/covers/no_cover.png')
    length = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    release_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.date.today())

    def __repr__(self):
        return f'<Album> {self.id} {self.name} {self.email}'
