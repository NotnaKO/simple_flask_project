import os
from logging import error, info

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

SqlAlchemyBase = declarative_base()

__factory = None


def global_init(db_file_name: str) -> None:
    """Create session with database"""
    global __factory

    if __factory:
        return

    db_file_name = db_file_name.strip()
    if not os.path.exists(db_file_name):
        error(f"{db_file_name} was not found")
        raise FileNotFoundError("No such file in directory")

    connection_address = f"sqlite:///{db_file_name}?check_same_thread=False"
    info(f"Connection with database by address: {connection_address}")

    engine = sqlalchemy.create_engine(connection_address, echo=False)
    __factory = sqlalchemy.orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


class BaseNotConnection(Exception):
    pass


def create_session() -> Session:
    if __factory is None:
        error("Database was not connect")
        raise BaseNotConnection("Database was not connect")
    return __factory()
