"""Flask configuration variables."""

from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config:
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")
    SECRET_KEY = environ.get("SECRET_KEY")
    TESTING = environ.get("TESTING")

    REPOSITORY = environ.get("REPOSITORY")

    # Database configuration: strip surrounding quotes if present
    raw_db_uri = environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///pets.db")
    SQLALCHEMY_DATABASE_URI = (
        raw_db_uri.strip().strip("'\"") if isinstance(raw_db_uri, str) else raw_db_uri
    )

    echo_string = environ.get("SQLALCHEMY_ECHO", "false")
    SQLALCHEMY_ECHO = False
    if isinstance(echo_string, str) and echo_string.lower().strip() == "true":
        SQLALCHEMY_ECHO = True
