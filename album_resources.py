from flask import abort, jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.albums import Album


def abort_if_album_not_found(album_id):
    session = db_session.create_session()
    album = session.query(Album).get(album_id)
    if not album:
        abort(404, message=f"Album {album_id} not found")


class AlbumsResource(Resource):
    def get(self, album_id):
        abort_if_album_not_found(album_id)
        session = db_session.create_session()
        album = session.query(Album).get(album_id)
        return jsonify({'album': album.to_dict()})

    def delete(self, album_id):
        abort_if_album_not_found(album_id)
        session = db_session.create_session()
        album = session.query(Album).get(album_id)
        session.delete(album)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('artist', required=True)
parser.add_argument('genre', required=True)
parser.add_argument('length', required=True)
parser.add_argument('release_date', required=True)
parser.add_argument('cover_url', required=False)


class AlbumsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        albums = session.query(Album).all()
        return jsonify({'albums': [item.to_dict() for item in albums]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if args['cover_url']:
            albums = Album(
                name=args['name'],
                artist=args['artist'],
                genre=args['genre'],
                length=args['length'],
                release_date=args['release_date'],
                cover_url=args['cover_url']
            )
        else:
            albums = Album(
                name=args['name'],
                artist=args['artist'],
                genre=args['genre'],
                length=args['length'],
                release_date=args['release_date']
            )
        session.add(albums)
        session.commit()
        return jsonify({'id': albums.id})
