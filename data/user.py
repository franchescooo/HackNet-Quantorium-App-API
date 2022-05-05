import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mail = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chats = sqlalchemy.Column(sqlalchemy.String, default="")
    img = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    extra = sqlalchemy.Column(sqlalchemy.String, default="")


class Chat(SqlAlchemyBase, UserMixin):
    __tablename__ = 'chat'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    users = sqlalchemy.Column(sqlalchemy.String, default="")
    msg = sqlalchemy.Column(sqlalchemy.String, default="")


class MSG(SqlAlchemyBase, UserMixin):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, default="")
    user = sqlalchemy.Column(sqlalchemy.Integer, default=0)
