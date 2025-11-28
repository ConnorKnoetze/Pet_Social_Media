from flask import (
    Blueprint,
    render_template,
)
from pets.adapters import repository
from pets.blueprints.authentication.authentication import login_required

post_bp = Blueprint("post", __name__)


def _repo():
    r = repository.repo_instance
    if r is None:
        raise RuntimeError("Repository not initialized")
    return r

@post_bp.route("/post/<int:id>")
@login_required
def view_post(id: int):
    repo = _repo()
    post = repo.get_post_by_id(id)
    user = repo.get_pet_user_by_id(post.user_id)
    if not post:
        return "User not found", 404
    # Adjusted template path to match actual location under pages/
    return render_template("pages/post/post.html", post=post, user=user)
