from dotenv import load_dotenv
from pets.adapters import repository

from pathlib import Path


def create_app():
    from flask import Flask


    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")

    data_path = (
            Path("pets") / "adapters" / "data"
    )  # this is pointing to our recipes.csv




    if app.config["REPOSITORY"] == "memory":
        # Create the MemoryRepository implementation for a memory-based repository.
        repository.repo_instance = MemoryRepository()
        database_mode = False  # (dont need this yet) but ill set is up to use later
        populate(data_path, repository.repo_instance, database_mode)

    @app.route("/")
    def home():
        return "Hello, Flask!"

    return app
