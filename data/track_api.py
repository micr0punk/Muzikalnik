from datetime import datetime

import flask
from flask import request, make_response, jsonify

from . import db_session
from .tracks import Track

blueprint = flask.Blueprint(
    'track_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/track/<int:track_id>', methods=['GET'])
def get_one_track(track_id):
    db_sess = db_session.create_session()
    track = db_sess.query(Track).get(track_id)
    if not track:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'track': track.to_dict()
        }
    )


@blueprint.route('/api/track', methods=['POST'])
def create_track():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['name', 'artist', 'genre', 'length', 'release_date', 'audio_url', 'album_id']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    print("Received data:", request.json)
    db_sess = db_session.create_session()

    data = request.json
    data['release_date'] = datetime.fromisoformat(data['release_date'])

    if request.json['cover_url']:
        track = Track(
            name=request.json['name'],
            artist=request.json['artist'],
            genre=request.json['genre'],
            length=request.json['length'],
            release_date=data['release_date'],
            cover_url=request.json['cover_url'],
            audio_url=request.json['audio_url'],
            album_id=request.json['album_id'],
            uploaded_from_user_id = request.json['uploaded_by_user']
        )
    else:
        track = Track(
            name=request.json['name'],
            artist=request.json['artist'],
            genre=request.json['genre'],
            length=request.json['length'],
            release_date=data['release_date'],
            audio_url=request.json['audio_url'],
            album_id=request.json['album_id'],
            uploaded_from_user_id=request.json['uploaded_by_user']
        )

    db_sess.add(track)
    db_sess.commit()

    return jsonify({'id': track.id}), 201


@blueprint.route('/api/track/<int:track_id>', methods=['DELETE'])
def delete_track(track_id):
    db_sess = db_session.create_session()
    track = db_sess.query(Track).get(track_id)
    if not track:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(track)
    db_sess.commit()
    return jsonify({'success': 'OK'})
