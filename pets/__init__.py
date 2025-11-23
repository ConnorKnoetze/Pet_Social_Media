from dotenv import load_dotenv
from pets.adapters import repository

from pathlib import Path

from pets.adapters.memory_repository import MemoryRepository
from pets.adapters.populate_repository import populate
from pets.blueprints.feed.feed import feed, feed_bp
from pets.blueprints.authentication.authentication import authentication_blueprint


def create_app():
    from flask import Flask

    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")

    if app.config["REPOSITORY"] == "memory":
        # Create the MemoryRepository implementation for a memory-based repository.
        repository.repo_instance = MemoryRepository()
        database_mode = False  # (dont need this yet) but ill set is up to use later
        populate(repository.repo_instance)

    app.register_blueprint(feed_bp)
    app.register_blueprint(authentication_blueprint)

    return app
