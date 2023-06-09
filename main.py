from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for, \
    send_from_directory
from data import db_session, news_api
from data.users import User
from data.news import News
from data.chats import Chats
from data.games import Games
from data.messages import Messages
from data.friends import Friends
from forms.register_form import RegisterForm
from forms.chat_form import ChatForm
from forms.login_form import LoginForm
from forms.news_form import NewsForm
from forms.add_games_form import AddGamesForm
from data.store_games import StoreGames
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


# главная страница (здесь отображаются новости)
@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


# регистрация аккаунта
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
        if " " in form.name.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Нельзя использовать пробел в имени")
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


# вход в аккаунт
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


# выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# окно добавления новости
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


# изменение новости
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


# удаление новости
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


# страница магазина
@app.route('/library', methods=['GET', 'POST'])
@login_required
def library():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        games = db_sess.query(Games).filter(
            (Games.user == current_user))
    else:
        games = db_sess.query(Games).filter(Games.is_private != True)
    return render_template("library.html", games=games)


# окно чатов
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    form = FriendsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        chats = Chats()
        currentuserid = str(current_user).split()[1]
        if str(form.friend_id.data).isnumeric():
            chats.user2 = form.friend_id.data
            chats.user1 = currentuserid
            if int(currentuserid) == int(chats.user2[0]):
                form.friend_id.errors.append("Это ты (У тебя нет друзей или что?)")
            elif db_sess.execute(text(f'select id from chats where '
                                      f'user1 == {chats.user2} and user2 == {currentuserid} or user2 == {chats.user2} '
                                      f'and user1 == {currentuserid}')).fetchall():
                form.friend_id.errors.append("Ты уже дружишь с ним")
            elif int(form.friend_id.data) > len(db_sess.execute(text('select name from users')).fetchall()):
                form.friend_id.errors.append("Пользователя не существует (как и твоих друзей)")
            else:
                chatid = db_sess.execute(text(f'select max(id) from chats')).fetchall()[0][0]
                if chatid is not None:
                    chats.id = int(chatid) + 1
                else:
                    chats.id = 1
                chats.name = db_sess.execute(text(f'select name from users '
                                                  f'where id == {chats.user2}')).fetchall()[0][0]
                chats.user_id = currentuserid
                current_user.chats.append(chats)
                db_sess.merge(current_user)
                db_sess.commit()
        else:
            if db_sess.execute(text(f'SELECT id FROM users WHERE name LIKE "{form.friend_id.data}"')).fetchall():
                ids = db_sess.execute(text(f'SELECT id FROM users WHERE name LIKE "{form.friend_id.data}"')).fetchall()[
                    0]
                id = str(ids)[1]
                chats.user2 = id
                chats.user1 = currentuserid
                if int(currentuserid) == int(chats.user2[0]):
                    form.friend_id.errors.append("Это ты (У тебя нет друзей или что?)")
                elif db_sess.execute(text(f'select id from chats where '
                                          f'user1 == {chats.user2} and user2 == {currentuserid} or user2 == '
                                          f'{chats.user2} '
                                          f'and user1 == {currentuserid}')).fetchall():
                    form.friend_id.errors.append("Ты уже дружишь с ним")
                else:
                    chatid = db_sess.execute(text(f'select max(id) from chats')).fetchall()[0][0]
                    if chatid is not None:
                        chats.id = int(chatid) + 1
                    else:
                        chats.id = 1
                    chats.name = db_sess.execute(text(f'select name from users '
                                                      f'where id == {chats.user2}')).fetchall()[0][0]
                    chats.user_id = currentuserid
                    current_user.chats.append(chats)
                    db_sess.merge(current_user)
                    db_sess.commit()
            else:
                form.friend_id.errors.append("Пользователя не существует (как и твоих друзей)")
    db_sess = db_session.create_session()
    currentuserid = str(current_user).split()[1]
    chatslist = db_sess.execute(text(f'select * from chats where user1 = {currentuserid} or '
                                     f'user2 = {currentuserid}')).fetchall()
    chatsreturn = []
    for elem in chatslist:
        chatsname1 = db_sess.execute(text(f'select name from users where id = {elem[1]}')).fetchall()[0][0]
        chatsname2 = db_sess.execute(text(f'select name from users where id = {elem[2]}')).fetchall()[0][0]
        chatsum = [chatsname1, chatsname2, elem[0], elem[1], elem[2]]
        chatsreturn.append(chatsum)
    return render_template('chatschild.html', title='Друзья и чаты',
                           form=form, news=chatsreturn)


# страница переписки
@app.route('/<variable>/chat', methods=['GET', 'POST'])
@login_required
def chatters(variable):
    form = ChatForm()
    db_sess = db_session.create_session()
    vari = variable.split(";")
    currentusername = str(current_user).split()[2]
    currentuseid = str(current_user).split()[1]
    if form.validate_on_submit():
        content = form.message.data
        chatid = vari[2]
        user1 = currentusername
        messages = Messages(content=content,
                            chatid=chatid,
                            username=user1)
        current_user.messages.append(messages)
        db_sess.merge(current_user)
        db_sess.commit()
        form.message.data = None
        return redirect(f"/{variable}/chat")
    id = str(current_user).split()[1]
    user = db_sess.query(User).filter_by(id=id).first()
    if currentusername not in variable.split(";")[:2]:
        return redirect("/")
    messages = db_sess.execute(text(f'select * from messages where chatid = {vari[2]}')).fetchall()
    return render_template("chat_dialogue.html", form=form, user=user, messages=messages,
                           curentusername=int(currentuseid))


# страница магазина
@app.route("/store")
def store():
    db_sess = db_session.create_session()
    store_games = db_sess.query(StoreGames)
    games = db_sess.query(Games)
    return render_template("store.html", store_games=store_games, games=games)


# добавление игры в магазин
@app.route('/add_games', methods=['GET', 'POST'])
@login_required
def adding_games():
    form = AddGamesForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        add_games = StoreGames()
        add_games.name = form.name.data
        add_games.description = form.description.data
        add_games.link = form.link.data
        current_user.store_games.append(add_games)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/store')
    return render_template('add_game.html', title='Добавление игры',
                           form=form)


# изменение описания игры в магазине
@app.route('/store_games/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_store_games(id):
    form = AddGamesForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        store_games = db_sess.query(StoreGames).filter(StoreGames.id == id,
                                                       StoreGames.user == current_user
                                                       ).first()
        if store_games:
            form.name.data = store_games.name
            form.description.data = store_games.description
            form.link.data = store_games.link
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        store_games = db_sess.query(StoreGames).filter(StoreGames.id == id,
                                                       StoreGames.user == current_user
                                                       ).first()
        if store_games:
            store_games.name = form.name.data
            store_games.description = form.description.data
            store_games.link = form.link.data
            db_sess.commit()
            return redirect('/store')
        else:
            abort(404)
    return render_template('add_game.html',
                           title='Редактирование игры',
                           form=form
                           )


# добавление игры из магазина
@app.route('/store_games_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def store_games_delete(id):
    db_sess = db_session.create_session()
    store_games = db_sess.query(StoreGames).filter(StoreGames.id == id,
                                                   StoreGames.user == current_user
                                                   ).first()
    if store_games:
        db_sess.delete(store_games)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/store')


# добавление игры из магазина в библиотеку
@app.route('/store_games_tolib/<int:id>', methods=['GET', 'POST'])
@login_required
def store_games_tolib(id):
    db_sess = db_session.create_session()
    currentuseid = str(current_user).split()[1]
    store_games = db_sess.query(StoreGames).filter(StoreGames.id == id).first()
    games = db_sess.query(Games).filter(Games.gameid == id, Games.user == current_user).first()
    if store_games:
        if not games:
            games = Games(
                gameid=store_games.id,
                title=store_games.name,
                link=store_games.link,
                user_id=currentuseid,
            )
            db_sess.add(games)
            db_sess.commit()
    else:
        abort(404)
    return redirect('/store')


# удаление игры из библиотеки
@app.route('/library_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def library_delete(id):
    db_sess = db_session.create_session()
    games = db_sess.query(Games).filter(Games.id == id,
                                        Games.user == current_user
                                        ).first()
    if games:
        db_sess.delete(games)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/library')


# переход в профиль
@app.route("/profile/<int:id>", methods=['GET', 'POST'])
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=id).first()
    return render_template("user_profile.html", user=user)


# переход в профиль из чата
@app.route("/profile_mini/<int:id>", methods=['GET', 'POST'])
def profile_mini(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=id).first()
    return render_template("profile_mini.html", user=user)


if __name__ == '__main__':
    main()
