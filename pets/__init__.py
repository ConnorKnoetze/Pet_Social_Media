from dotenv import load_dotenv
from flask import render_template, app

from pets.adapters import repository

from pathlib import Path

from pets.adapters.memory_repository import MemoryRepository
from pets.adapters.populate_repository import populate
from pets.blueprints.feed.feed import feed, feed_bp
from pets.blueprints.authentication.authentication import authentication_blueprint
from pets.blueprints.user.user import user_bp
from pets.utilities.auth import get_current_user
from pets.utilities.timeago import timeago


def create_app():
    from flask import Flask

    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("/pages/errors/404.html"), 404

    if app.config["REPOSITORY"] == "memory":
        # Create the MemoryRepository implementation for a memory-based repository.
        repository.repo_instance = MemoryRepository()
        database_mode = False  # (dont need this yet) but ill set is up to use later
        populate(repository.repo_instance)

    app.register_blueprint(feed_bp)
    app.register_blueprint(authentication_blueprint)
    app.register_blueprint(user_bp)


    app.jinja_env.filters["timeago"] = timeago

    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user()}

    #
    # @app.before_request
    # def before_flask_http_request_function():
    #     if isinstance(repository.repo_instance, SqlAlchemyRepository):
    #         repository.repo_instance.reset_session()
    #
    # # Register a tear-down method that will be called after each request has been processed.
    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     if isinstance(repository.repo_instance, SqlAlchemyRepository):
    #         repository.repo_instance.close_session()

    return app
