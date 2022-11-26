import datetime

import sqlalchemy.orm
import werkzeug.security
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    """User database class"""
    __table_name__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    surname = Column(String, nullable=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    position = Column(Integer, default=3)
    address = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    modified_date = Column(DateTime, default=datetime.datetime.now())
    notes = sqlalchemy.orm.relation("Notes", back_populates="user")

    def __repr__(self):
        return f"{self.surname} {self.name} with email {self.email}"

    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, value):
        self.hashed_password = werkzeug.security.generate_password_hash(value)

    def check_password(self, value):
        return werkzeug.security.check_password_hash(self.hashed_password, value)
