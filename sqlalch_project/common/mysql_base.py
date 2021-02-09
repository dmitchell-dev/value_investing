from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


db_username = os.environ["DJANGO_DB_USERNAME"]
db_password = os.environ["DJANGO_DB_PASSWORD"]
db_name = os.environ["DJANGO_DB_NAME"]

connection_string = f"mysql://{db_username}:{db_password}@localhost/{db_name}"
engine = create_engine(connection_string)

_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
