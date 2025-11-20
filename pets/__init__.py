from pets.blueprints.feed.feed import feed, feed_bp


def create_app():
    from flask import Flask

    app = Flask(__name__)

    app.register_blueprint(feed_bp)

    return app
