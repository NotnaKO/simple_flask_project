import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Notes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(Integer, ForeignKey("users.id"))
    header = Column(String, nullable=True)
    category = orm.relation("Category", secondary="category_association", backref="news")
    text_address = Column(String)
    modified_date = Column(DateTime, default=datetime.datetime.now)
    user = orm.relation('User')
