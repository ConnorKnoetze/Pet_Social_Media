import os

from flask import (
    Blueprint,
    render_template,
)
from pets.blueprints.authentication.authentication import login_required
from pets.blueprints.services import _repo

post_bp = Blueprint("post", __name__)


@post_bp.route("/post/<int:id>")
@login_required
def view_post(id: int):
    repo = _repo()
    post = repo.get_post_by_id(id)
    user = repo.get_pet_user_by_id(post.user_id)
    if not post:
        return "User not found", 404

    post_path = (
        os.path.join("../", post.media_path)
        if user.username in str(post.media_path)
        else post.media_path
    )
    # Adjusted template path to match actual location under pages/
    return render_template(
        "pages/post/post.html", post=post, user=user, post_path=post_path
    )
