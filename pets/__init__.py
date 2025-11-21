from dotenv import load_dotenv
from pets.adapters import repository

from pathlib import Path

from pets.adapters.memory_repository import MemoryRepository
from pets.adapters.populate_repository import populate


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

    @app.route("/")
    def home():
        return "Hello, Flask!"

    return app
