from dotenv import load_dotenv
from flask import render_template
from sqlalchemy import NullPool, create_engine, inspect, text
from sqlalchemy.orm import clear_mappers, sessionmaker

from pets.adapters import repository
from pets.adapters.database_repository import SqlAlchemyRepository

from pets.adapters.memory_repository import MemoryRepository
from pets.adapters.orm import map_model_to_tables, mapper_registry
from pets.adapters.populate_repository import populate
from pets.blueprints.feed.feed import feed, feed_bp
from pets.blueprints.authentication.authentication import authentication_blueprint
from pets.blueprints.upload.upload import upload_bp
from pets.blueprints.user.user import user_bp
from pets.blueprints.post.post import post_bp
from pets.utilities.auth import get_current_user
from pets.utilities.timeago import timeago
import pets.adapters.orm as orm


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

    elif app.config["REPOSITORY"] == "database":
        database_uri = app.config["SQLALCHEMY_DATABASE_URI"]

        database_echo = app.config["SQLALCHEMY_ECHO"]
        if database_uri.startswith("sqlite"):
            database_engine = create_engine(
                database_uri,
                connect_args={"check_same_thread": False},
                poolclass=NullPool,
                echo=database_echo,
            )
        else:
            database_engine = create_engine(
                database_uri,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=database_echo,
            )


        session_factory = sessionmaker(
            autocommit=False, autoflush=True, bind=database_engine
        )

        inspector = inspect(database_engine)

        # Always clear and remap (idempotent for app restarts)

        clear_mappers()

        map_model_to_tables()

        if len(inspector.get_table_names()) == 0:
            print("No tables found — creating tables and populating database...")

            mapper_registry.metadata.create_all(database_engine)

            repository.repo_instance = SqlAlchemyRepository(
                session_factory, database_uri
            )

            database_mode = True

            populate(repository.repo_instance, database_mode)

        else:
            print("Tables found")

            repository.repo_instance = SqlAlchemyRepository(
                session_factory, database_uri
            )

    app.register_blueprint(feed_bp)
    app.register_blueprint(authentication_blueprint)
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(upload_bp)

    app.jinja_env.filters["timeago"] = timeago

    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user()}

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if isinstance(repository.repo_instance, SqlAlchemyRepository):
            repository.repo_instance.close_session()

    return app
