from flask import Blueprint, render_template

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/')
def feed():
    """Render the feed page."""
    return render_template("pages/feed.html")