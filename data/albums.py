import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Album(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'albums'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    artist = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    length = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    release_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.date.today())
    cover_url = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='/static/covers/no_cover.png')
    uploaded_from_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    tracks = orm.relationship("Track", back_populates="album")

    def __repr__(self):
        return f'<Album> {self.id} {self.name} {self.artist}'
