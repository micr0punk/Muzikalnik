import requests
from flask import Flask, render_template, flash, redirect, url_for, make_response, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api
from werkzeug.security import generate_password_hash

import user_resources
from data import db_session, user_api
from data.albums import Album
from data.tracks import Track
from data.users import User
from forms.index_form import SearchForm
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.upload_form import UploadAlbumForm, UploadTrackForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)

api.add_resource(user_resources.UsersListResource, '/api/v2/users')

api.add_resource(user_resources.UsersResource, '/api/v2/users/<int:user_id>')

login_manager = LoginManager()
login_manager.init_app(app)

cover_folder = 'static/covers'
allowed_extensions = {'png', 'jpg', 'jpeg'}

db_session.global_init("db/global.db")

app.config['cover_folder'] = cover_folder


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
            return redirect(url_for('login'))
        else:
            flash("Ошибка при регистрации. Повторите попытку.", "danger")

    return render_template('register.html', title='Регистрация – Муызкальник', form=form)


@app.route('/search')
def search():
    albums = []
    return render_template('search.html', title='Поиск – Музыкальник', results=albums)


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


@app.route("/upload/<int:user_id>", methods=['GET', 'POST'])
@login_required
def upload(user_id):
    album_form = UploadAlbumForm()
    track_form = UploadTrackForm()

    albums = db_session.create_session().query(Album).filter_by(uploaded_from_user_id=current_user.id).all()
    track_form.album_id.choices = [(0, 'Не относится к альбому')] + [(a.id, a.name) for a in albums]

    if album_form.validate_on_submit() and album_form.submit.data:
        pass

    elif track_form.validate_on_submit() and track_form.submit.data:
        pass

    return render_template('upload.html', title='Загрузка релиза – Музыкальник',
                           album_form=album_form,
                           track_form=track_form)


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


def main_api():
    db_session.global_init("db/global.db")
    app.register_blueprint(user_api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main_api()
