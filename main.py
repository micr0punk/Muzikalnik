import os

import requests
from flask import Flask, render_template, flash, redirect, url_for, make_response, jsonify, abort, send_file
from flask_login import login_user, LoginManager, login_required, logout_user
from flask_restful import Api
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

import album_resources
import track_resources
import user_resources
from data import db_session, user_api, track_api, album_api
from data.albums import Album
from data.tracks import Track
from data.users import User
from forms.index_form import SearchForm
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.upload_form import UploadAlbumForm, UploadTrackForm

COVER_FOLDER = 'static/covers'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# ALBUM_FOLDER = 'static/covers'
TRACKS_FOLDER = 'static/tracks'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['COVER_UPLOAD_FOLDER'] = COVER_FOLDER
# app.config['ALBUM_UPLOAD_FOLDER'] = ALBUM_FOLDER
app.config['TRACK_UPLOAD_FOLDER'] = TRACKS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

api = Api(app)

api.add_resource(user_resources.UsersListResource, '/api/v2/users')
api.add_resource(user_resources.UsersResource, '/api/v2/users/<int:user_id>')

api.add_resource(album_resources.AlbumsListResource, '/api/v2/albums')
api.add_resource(album_resources.AlbumsResource, '/api/v2/albums/<int:album_id>')

api.add_resource(track_resources.TracksListResource, '/api/v2/tracks')
api.add_resource(track_resources.TracksResource, '/api/v2/tracks/<int:track_id>')

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/global.db")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_next_image_id():
    files = os.listdir('static/covers')
    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]

    if not image_files:
        return 1

    max_number = 0
    for file in image_files:
        try:
            number = int(file.split('.')[0])
            max_number = max(number, max_number)
        except ValueError:
            continue

    return max_number + 1


def get_next_song_id():
    files = os.listdir('static/tracks')
    track_files = [f for f in files if f.endswith(('.mp3', '.wav', '.ogg', 'm4a'))]

    if not track_files:
        return 1

    max_number = 0
    for file in track_files:
        try:
            number = int(file.split('.')[0])
            max_number = max(number, max_number)
        except ValueError:
            continue

    return max_number + 1


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
def index():
    form = SearchForm()
    db_sess = db_session.create_session()

    albums = db_sess.query(Album).all()
    tracks = db_sess.query(Track).all()

    return render_template("index.html", title='Муызкальник', form=form, albums=albums,
                           tracks=tracks)


@app.route('/search_album')
def search_album():
    form = SearchForm()
    db_sess = db_session.create_session()

    albums = db_sess.query(Album).all()

    return render_template('search_album.html', title='Поиск – Музыкальник', form=form, results=albums)


@app.route('/search_track')
def search_track():
    form = SearchForm()
    db_sess = db_session.create_session()

    albums = db_sess.query(Album).all()
    tracks = db_sess.query(Track).all()

    return render_template('search_track.html', title='Поиск – Музыкальник', form=form, results=tracks, albums=albums)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация – Муызкальник', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = {'name': form.username.data,
                'about': form.about.data,
                'email': form.email.data,
                'hashed_password': generate_password_hash(form.password.data),
                }
        response = requests.post('http://localhost:8080/api/user', json=data)
        print(response.status_code)
        if response.status_code == 201:
            return redirect(url_for('index'))
        else:
            flash("Ошибка при регистрации. Повторите попытку.", "danger")

    return render_template('register.html', title='Регистрация – Муызкальник', form=form)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return render_template('profile.html', title='Профиль – Музыкальник', user=user)


@app.route('/edit_profile')
def edit_profile():
    return 'ABRACADABRA'


@app.route('/album_detail/<int:album_id>')
def album_detail(album_id):
    db_sess = db_session.create_session()
    for album in db_sess.query(Album).filter(Album.id == album_id):
        return render_template('album_page.html', title='О релизе – Муызкальник', album=album)


@app.route('/track_detail/<int:track_id>')
def track_detail(track_id):
    db_sess = db_session.create_session()
    for track in db_sess.query(Track).filter(Track.id == track_id):
        if Track.album_id != 0:
            album = db_sess.query(Album).filter(Album.id == track.album_id).first()
            return render_template('track_page.html', title='О релизе – Муызкальник', track=track,
                                   album=album)
        else:
            return render_template('track_page.html', title='О релизе – Муызкальник', track=track,
                                   album=[])


@app.route('/download/<int:track_id>')
@login_required
def download(track_id):
    db_sess = db_session.create_session()
    track = db_sess.query(Track).filter(Track.id == track_id).first()

    if not track:
        abort(404)

    file_path = track.audio_url.lstrip("/")
    abs_path = os.path.join(os.getcwd(), file_path)

    if not os.path.exists(abs_path):
        abort(404)

    extension = os.path.splitext(abs_path)[-1]
    download_filename = f"{track.artist} - {track.name}{extension}"

    return send_file(abs_path, as_attachment=True, download_name=download_filename)


@app.route('/listen/<int:track_id>')
@login_required
def listen(track_id):
    db_sess = db_session.create_session()
    track = db_sess.query(Track).get(track_id)
    if not track:
        abort(404)

    file_path = track.audio_url.lstrip("/")
    abs_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(abs_path):
        abort(404)

    return send_file(abs_path)


@app.route("/upload/<int:user_id>", methods=['GET', 'POST'])
@login_required
def upload(user_id):
    album_form = UploadAlbumForm()
    track_form = UploadTrackForm()

    albums = db_session.create_session().query(Album).all()
    track_form.album_id.choices = [(0, 'Не относится к альбому')] + [(a.id, a.name) for a in albums]
    albums_with_covers = [(0, 'Не относится к альбому', '/static/no_album.png')] + [
        (a.id, a.name, a.cover_url or '/static/no_cover.png') for a in albums
    ]
    if album_form.validate_on_submit() and album_form.form_name.data == 'album':
        db_sess = db_session.create_session()
        similar = db_sess.query(Album).filter(Album.name == album_form.name.data,
                                              Album.artist == album_form.artist.data).first()
        if similar:
            flash("Такой релиз уже есть на сайте :(", "danger")
            return redirect(url_for('index'))

        cover_file = album_form.cover.data

        if cover_file and allowed_file(cover_file.filename):
            filename = secure_filename(cover_file.filename)
            cover_save_filename = f"{get_next_image_id()}.png"
            save_path = os.path.join(app.config['COVER_UPLOAD_FOLDER'], cover_save_filename)
            cover_file.save(save_path)
            cover_url = f"/static/covers/{cover_save_filename}"

        if album_form.cover.data:
            album_data = {'name': album_form.name.data,
                          'artist': album_form.artist.data,
                          'genre': album_form.genre.data,
                          'length': album_form.length.data,
                          'release_date': album_form.release_date.data.strftime('%Y-%m-%d'),
                          'cover_url': cover_url,
                          'uploaded_by_user': user_id
                          }
        else:
            album_data = {'name': album_form.name.data,
                          'artist': album_form.artist.data,
                          'genre': album_form.genre.data,
                          'length': album_form.length.data,
                          'release_date': album_form.release_date.data.strftime('%Y-%m-%d'),
                          'cover_url': [],
                          'uploaded_by_user': user_id
                          }

        response = requests.post('http://localhost:8080/api/album', json=album_data)
        print(response.status_code)
        if response.status_code == 201:
            flash("Релиз добавлен успешно!", "success")
            return redirect(url_for('index'))
        else:
            flash("Ошибка при добавлении. Повторите попытку.", "danger")

    elif track_form.validate_on_submit() and track_form.form_name.data == 'track':
        print("Track form data:", track_form.data)
        print("Track form errors:", track_form.errors)
        db_sess = db_session.create_session()
        similar = db_sess.query(Track).filter(Track.name == track_form.name.data,
                                              Track.artist == track_form.artist.data).first()
        if similar:
            flash("Такой релиз уже есть на сайте :(", "danger")
            return redirect(url_for('index'))

        cover_file = track_form.cover.data
        if cover_file and allowed_file(cover_file.filename):
            filename = secure_filename(cover_file.filename)
            cover_save_filename = f"{get_next_image_id()}.png"
            save_path = os.path.join(app.config['COVER_UPLOAD_FOLDER'], cover_save_filename)
            cover_file.save(save_path)

            cover_url = f"/static/covers/{cover_save_filename}"

        track_file = track_form.audio_file.data

        filename = secure_filename(track_file.filename)
        track_save_filename = f"{get_next_song_id()}.{filename.rsplit('.', 1)[-1]}"
        save_path = os.path.join(app.config['TRACK_UPLOAD_FOLDER'], track_save_filename)
        track_file.save(save_path)

        track_url = f"/static/tracks/{track_save_filename}"

        if track_form.cover.data:
            track_data = {'name': track_form.name.data,
                          'artist': track_form.artist.data,
                          'genre': track_form.genre.data,
                          'length': track_form.length.data,
                          'release_date': track_form.release_date.data.strftime('%Y-%m-%d'),
                          'cover_url': cover_url,
                          'audio_url': track_url,
                          'album_id': track_form.album_id.data,
                          'uploaded_by_user': user_id
                          }
        else:
            track_data = {'name': track_form.name.data,
                          'artist': track_form.artist.data,
                          'genre': track_form.genre.data,
                          'length': track_form.length.data,
                          'release_date': track_form.release_date.data.strftime('%Y-%m-%d'),
                          'cover_url': [],
                          'audio_url': track_url,
                          'album_id': track_form.album_id.data,
                          'uploaded_by_user': user_id
                          }

        response = requests.post('http://localhost:8080/api/track', json=track_data)
        print(response.status_code)
        if response.status_code == 201:
            flash("Релиз добавлен успешно!", "success")
            return redirect(url_for('index'))
        else:
            flash("Ошибка при добавлении. Повторите попытку.", "danger")

    return render_template('upload.html', title='Загрузка релиза – Музыкальник',
                           album_form=album_form,
                           track_form=track_form,
                           albums_with_covers=albums_with_covers)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'Размер файла превышает допустимый лимит', 413


def main_api():
    db_session.global_init("db/global.db")
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(track_api.blueprint)
    app.register_blueprint(album_api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main_api()
