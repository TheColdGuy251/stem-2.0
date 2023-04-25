import flask
from . import db_session
from .store_games import StoreGames
from flask import jsonify, request

blueprint = flask.Blueprint(
    'store_games_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/store_games', methods=['GET'])
def get_news():
    db_sess = db_session.create_session()
    store_games = db_sess.query(StoreGames).all()
    return jsonify(
        {
            'store_games':
                [item.to_dict(only=('name', 'description', 'user.name'))
                 for item in store_games]
        }
    )


@blueprint.route('/api/store_games/<int:store_games_id>', methods=['GET'])
def get_one_news(store_games_id):
    db_sess = db_session.create_session()
    store_games = db_sess.query(StoreGames).get(store_games_id)
    if not store_games:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'news': store_games.to_dict(only=(
                'name', 'description', 'user_id', 'link'))
        }
    )


@blueprint.route('/api/store_games', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'description', 'user_id', 'link']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    store_games = StoreGames(
        name=request.json['name'],
        description=request.json['description'],
        user_id=request.json['user_id'],
        link=request.json['link']
    )
    db_sess.add(store_games)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/store_games/<int:store_games_id>', methods=['DELETE'])
def delete_news(store_games_id):
    db_sess = db_session.create_session()
    store_games = db_sess.query(StoreGames).get(store_games_id)
    if not store_games:
        return jsonify({'error': 'Not found'})
    db_sess.delete(store_games)
    db_sess.commit()
    return jsonify({'success': 'OK'})