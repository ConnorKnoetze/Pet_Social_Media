import os

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

        database_engine = create_engine(
            database_uri,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
            echo=database_echo,
        )

        session_factory = sessionmaker(
            autocommit=False, autoflush=True, bind=database_engine
        )

        orm.init_db(database_engine)
        # inspect before creating tables so we only populate when the DB is truly empty

        inspector = inspect(database_engine)

        # ensure mappers are registered so create_all() knows the tables to create

        def _debug_database_state(database_uri, engine, mapper_registry, label=""):
            print(f"DEBUG({label}) DB URI repr:", repr(database_uri))
            print(
                f"DEBUG({label}) ENV raw SQLALCHEMY_DATABASE_URI:",
                repr(os.environ.get("SQLALCHEMY_DATABASE_URI")),
            )
            print(
                f"DEBUG({label}) mapped tables:",
                list(mapper_registry.metadata.tables.keys()),
            )
            try:
                inspector = inspect(engine)
                print(f"DEBUG({label}) inspector tables:", inspector.get_table_names())
            except Exception as e:
                print(f"DEBUG({label}) inspector error:", e)

        clear_mappers()

        map_model_to_tables()
        _debug_database_state(
            database_uri, database_engine, mapper_registry, "before_create_all"
        )


        if len(inspector.get_table_names()) == 0:
            print("No tables found — creating tables and populating database...")

            mapper_registry.metadata.create_all(database_engine)
            _debug_database_state(
                database_uri, database_engine, mapper_registry, "after_create_all"
            )


            # create repository after mappings/tables exist

            repository.repo_instance = SqlAlchemyRepository(session_factory)

            # populate initial data in database mode

            database_mode = True

            populate(repository.repo_instance, database_mode)
            try:
                with database_engine.connect() as conn:
                    for t in ("pet_users", "posts", "comments", "likes", "users"):
                        try:
                            cnt = conn.execute(
                                text(f"SELECT count(*) FROM {t}")
                            ).scalar()
                            print(f"DEBUG rows in {t}: {cnt}")
                        except Exception as e:
                            print(f"DEBUG cannot count {t}: {e}")
            except Exception as e:
                print("DEBUG connection error when counting rows:", e)

        else:
            print("Tables found")

            # repository can be created now (mappers already registered above)

            repository.repo_instance = SqlAlchemyRepository(session_factory)

    app.register_blueprint(feed_bp)
    app.register_blueprint(authentication_blueprint)
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)

    app.jinja_env.filters["timeago"] = timeago

    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user()}

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if isinstance(repository.repo_instance, SqlAlchemyRepository):
            repository.repo_instance.close_session()

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
