import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Chats(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user1 = sqlalchemy.Column(sqlalchemy.Integer)
    user2 = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.Text)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def __repr__(self):
        return f'<Chats> {self.id} {self.user1} {self.user2}'