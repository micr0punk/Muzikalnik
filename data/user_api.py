from datetime import datetime

import flask
from flask import request, make_response, jsonify

from . import db_session
from .users import User

blueprint = flask.Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/user/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'user': user.to_dict(only=(
                'id', 'name', 'about', 'email', 'hashed_password', 'created_date'))
        }
    )


@blueprint.route('/api/user', methods=['POST'])
def create_user():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['name', 'about', 'email', 'hashed_password']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    print("Received data:", request.json)
    db_sess = db_session.create_session()

    # created_date = datetime.fromisoformat(request.json['created_date'])

    user = User(
        name=request.json['name'],
        about=request.json['about'],
        email=request.json['email'],
        hashed_password=request.json['hashed_password'],
    )

    db_sess.add(user)
    db_sess.commit()

    return jsonify({'id': user.id}), 201


@blueprint.route('/api/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})
