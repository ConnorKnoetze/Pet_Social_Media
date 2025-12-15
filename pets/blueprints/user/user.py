import os
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
from werkzeug.utils import secure_filename

user_bp = Blueprint("user", __name__)


def _repo():
    r = repository.repo_instance
    if r is None:
        raise RuntimeError("Repository not initialized")
    return r

PROJECT_ROOT = Path(__file__).parent.parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / "static" / "images" / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

@user_bp.route("/<int:user_id>/settings", methods=["GET", "POST"])
@login_required
def user_settings(user_id: int):
    repo = _repo()
    username = session.get("user_name")
    if not username:
        return redirect(url_for("authentication.login"))

    user = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(username)
    if request.method == "POST":
        if not user or user.id != user_id:
            return "Unauthorized", 403
        # Process form data and update user settings

        # process profile picture upload
        file = request.files.get("profile_picture")
        if file and allowed_file(file.filename):
            user_folder = UPLOAD_FOLDER / username
            user_folder.mkdir(parents=True, exist_ok=True)
            filename = f"user_{user_id}_" + secure_filename(file.filename)
            full_path = user_folder / filename
            file.save(full_path)
            if full_path.exists():
                static_root = PROJECT_ROOT / "static"
                rel_path = full_path.relative_to(static_root)
                user.profile_picture_path = url_for(
                    "static", filename=str(rel_path).replace("\\", "/")
                )


        #process bio update
        new_bio = request.form.get("bio", "")
        if len(new_bio) > 255:
            return "Bio must be 255 characters or less", 400
        user.bio = new_bio

        #update user in repo
        repo.update_user(user)
        return redirect(url_for("user.view_user_profile", username=user.username))
    return render_template("pages/user/settings.html", user=user)

@user_bp.route("/user/<string:username>/followers")
@login_required
def view_followers(username: str):
    repo = _repo()
    user = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(username)
    if not user:
        return "User not found", 404
    followers = repo.get_followers(user)
    return render_template("pages/user/followers.html", user=user, followers=followers)