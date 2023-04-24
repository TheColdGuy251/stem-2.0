import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class StoreGames(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'store_games'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    released = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def __repr__(self):
        return f'<Store_Games> {self.id} {self.name} {self.description} {self.link}'