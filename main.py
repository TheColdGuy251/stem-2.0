from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify
from data import db_session, news_api
from data.users import User
from data.news import News
from data.games import Games
from data.friends import Friends
from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from forms.news_form import NewsForm
from forms.friends_form import FriendsForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_api.blueprint)
    app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/library', methods=['GET', 'POST'])
@login_required
def library():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('library.html', title='Библиотека',
                           form=form)


@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('friends.html', title='Друзья',
                           form=form)


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    form = FriendsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        friends = Friends()
        currentuserid = str(current_user).split()[1]
        if str(form.friend_id.data).isnumeric():
            friends.id = form.friend_id.data
            if db_sess.execute(text(f'select id from friends where id == {form.friend_id.data} '
                                    f'and user_id == {currentuserid}')).fetchall():
                form.friend_id.errors.append("Ты уже дружишь с ним")
            elif int(currentuserid) == int(friends.id[0]):
                form.friend_id.errors.append("Это ты (У тебя нет друзей или что?)")
            elif int(form.friend_id.data) > len(db_sess.execute(text('select name from users')).fetchall()):
                form.friend_id.errors.append("Пользователя не существует (как и твоих друзей)")
            else:
                friends.chat = db_sess.execute(text(f'select max(chat) from friends')).fetchall()[0][0]
                if friends.chat is not None:
                    friends.chat += 1
                else:
                    friends.chat = 0
                friends.name = db_sess.execute(text(f'select name from users '
                                                    f'where id == {friends.id}')).fetchall()[0][0]
                friends.last_played = None
                friends.user_id = currentuserid
                current_user.friends.append(friends)
                db_sess.merge(current_user)
                db_sess.commit()
        else:
            if db_sess.execute(text(f'SELECT id FROM users WHERE name LIKE "{form.friend_id.data}"')).fetchall():
                ids = db_sess.execute(text(f'SELECT id FROM users WHERE name LIKE "{form.friend_id.data}"')).fetchall()[0]
                id = str(ids)[1]
                friends.id = id
                if db_sess.execute(text(f'select id from friends where id == {friends.id[0]} '
                                        f'and user_id == {currentuserid}')).fetchall():
                    form.friend_id.errors.append("Ты уже дружишь с ним")
                elif int(currentuserid) == int(friends.id[0]):
                    form.friend_id.errors.append("Это ты (У тебя нет друзей или что?)")
                else:
                    friends.chat = db_sess.execute(text(f'select max(chat) from friends')).fetchall()[0][0]
                    if friends.chat is not None:
                        friends.chat += 1
                    else:
                        friends.chat = 0
                    friends.name = db_sess.execute(text(f'select name from users where '
                                                    f'id == {int(friends.id[0])}')).fetchall()[0][0]
                    friends.last_played = None
                    friends.user_id = currentuserid
                    current_user.friends.append(friends)
                    db_sess.merge(current_user)
                    db_sess.commit()
            else:
                form.friend_id.errors.append("Пользователя не существует (как и твоих друзей)")
    return render_template('chat.html', title='Друзья и чаты',
                           form=form)


if __name__ == '__main__':
    main()
