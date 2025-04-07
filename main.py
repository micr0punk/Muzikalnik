import os

from flask import Flask, render_template, flash, redirect, url_for
from flask_login import login_user, LoginManager
from werkzeug.utils import secure_filename

from data import db_session
from data.users import User
from forms.index_form import SearchForm
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.upload_album_form import UploadAlbumForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

cover_folder = 'static/covers'
allowed_extensions = {'png', 'jpg', 'jpeg'}

db_session.global_init("db/global.db")

app.config['cover_folder'] = cover_folder


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    form = SearchForm()

    albums = [
        {
            'title': 'Test Album',
            'artist': 'Unknown Artist',
            'genre': 'Rock',
            'cover_url': '/static/test_cover.jpg',
            'id': 1
        }
    ]

    return render_template("index.html", form=form, albums=albums)


@app.route("/login")
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


@app.route('/register')
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return "<h3>Вы зарегистрированы! (заглушка)</h3>"
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

        # Здесь можешь сохранить данные альбома в базу
        flash("Альбом успешно загружен!", "success")
        return redirect(url_for('index'))

    return render_template("upload.html", form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
