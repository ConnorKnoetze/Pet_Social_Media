from pathlib import Path
from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    session,
    redirect,
    url_for,
)
from pets.adapters import repository
from pets.blueprints.authentication.authentication import login_required
from pets.domainmodel.PetUser import PetUser

user_bp = Blueprint("user", __name__)


def _repo():
    r = repository.repo_instance
    if r is None:
        raise RuntimeError("Repository not initialized")
    return r


@user_bp.route("/user/<string:username>")
@login_required
def view_user_profile(username: str):
    repo = _repo()
    user = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(username)
    if not user:
        return "User not found", 404
    # Adjusted template path to match actual location under pages/
    posts = [post for post in user.posts if post.media_type == "photo"]
    return render_template("pages/user/profile.html", user=user, posts=posts)
