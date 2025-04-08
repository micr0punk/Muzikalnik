import os
from datetime import datetime

from flask import Flask, render_template, flash, redirect, url_for, make_response, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user
from flask_restful import Api
from requests import post
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

import user_resources
from data import db_session, user_api
from data.users import User
from forms.index_form import SearchForm
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.upload_album_form import UploadAlbumForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)

# для списка объектов
api.add_resource(user_resources.UsersListResource, '/api/v2/users')

# для одного объекта
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

    albums = [
        {
            'id': 1,
            'name': 'Тестовое название',
            'artist': 'Unknown Artist',
            'genre': 'Рок',
            'cover_url': '/static/covers/no_cover.png',
            'length': '48:20'
        }
    ]

    return render_template("index.html", title='Музыкальник', form=form, albums=albums)


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
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        response = post('http://localhost:5000/api/user',
                        json={'name': form.username.data,
                              'about': form.about.data,
                              'email': form.email.data,
                              'hashed_password': generate_password_hash(form.password.data),
                              'created_date': datetime.now().isoformat()})
        if response.status_code == 201:
            return redirect(url_for('login'))
        else:
            flash("Ошибка при регистрации. Повторите попытку.", "danger")

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/search')
def search():
    return "<h2>Здесь будет форма поиска</h2>"


@app.route('/album_detail')
def album_detail():
    return "<h2>Здесь будет форма поиска</h2>"


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    form = UploadAlbumForm()
    if form.validate_on_submit():
        file = form.cover.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash("Альбом успешно загружен!", "success")
        return redirect(url_for('index'))

    return render_template("upload.html", form=form)


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
