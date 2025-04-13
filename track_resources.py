from flask import abort, jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.tracks import Track


def abort_if_track_not_found(track_id):
    session = db_session.create_session()
    track = session.query(Track).get(track_id)
    if not track:
        abort(404, message=f"Track {track_id} not found")


class TracksResource(Resource):
    def get(self, track_id):
        abort_if_track_not_found(track_id)
        session = db_session.create_session()
        track = session.query(Track).get(track_id)
        return jsonify({'track': track.to_dict()})

    def delete(self, track_id):
        abort_if_track_not_found(track_id)
        session = db_session.create_session()
        track = session.query(Track).get(track_id)
        session.delete(track)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('artist', required=True)
parser.add_argument('genre', required=True)
parser.add_argument('length', required=True)
parser.add_argument('release_date', required=True)
parser.add_argument('cover_url', required=False)
parser.add_argument('audio_url', required=True)
parser.add_argument('album_id', required=False)

class TracksListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tracks = session.query(Track).all()
        return jsonify({'tracks': [item.to_dict() for item in tracks]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if args['cover_url']:
            tracks = Track(
                name=args['name'],
                artist=args['artist'],
                genre=args['genre'],
                length=args['length'],
                release_date=args['release_date'],
                cover_url=args['cover_url'],
                audio_url = args['audio_url'],
                album_id = args['album_id']
            )
        else:
            tracks = Track(
                name=args['name'],
                artist=args['artist'],
                genre=args['genre'],
                length=args['length'],
                release_date=args['release_date'],
                audio_url = args['audio_url'],
                album_id = args['album_id']
            )
        session.add(tracks)
        session.commit()
        return jsonify({'id': tracks.id})
