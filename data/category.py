from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase

category_association_table = Table('category_association', SqlAlchemyBase.metadata,
                                   Column('notes', Integer, ForeignKey('notes.id')),
                                   Column('category', Integer, ForeignKey('category.id')))


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
