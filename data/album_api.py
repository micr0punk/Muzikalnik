from datetime import datetime

import flask
from flask import request, make_response, jsonify

from . import db_session
from .albums import Album

blueprint = flask.Blueprint(
    'album_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/album/<int:album_id>', methods=['GET'])
def get_one_album(album_id):
    db_sess = db_session.create_session()
    album = db_sess.query(Album).get(album_id)
    if not album:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'album': album.to_dict()
        }
    )


@blueprint.route('/api/album', methods=['POST'])
def create_album():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['name', 'artist', 'genre', 'length', 'release_date']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    print("Received data:", request.json)
    db_sess = db_session.create_session()

    data = request.json
    data['release_date'] = datetime.fromisoformat(data['release_date'])

    if request.json['cover_url']:
        album = Album(
            name=request.json['name'],
            artist=request.json['artist'],
            genre=request.json['genre'],
            length=request.json['length'],
            release_date=data['release_date'],
            cover_url=request.json['cover_url'],
            uploaded_from_user_id=request.json['uploaded_by_user']
        )
    else:
        album = Album(
            name=request.json['name'],
            artist=request.json['artist'],
            genre=request.json['genre'],
            length=request.json['length'],
            release_date=data['release_date'],
            uploaded_from_user_id = request.json['uploaded_by_user']
        )

    db_sess.add(album)
    db_sess.commit()

    return jsonify({'id': album.id}), 201


@blueprint.route('/api/album/<int:album_id>', methods=['DELETE'])
def delete_album(album_id):
    db_sess = db_session.create_session()
    album = db_sess.query(Album).get(album_id)
    if not album:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(album)
    db_sess.commit()
    return jsonify({'success': 'OK'})
