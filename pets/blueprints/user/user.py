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
from pets.domainmodel.PetUser import PetUser

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

        #process profile picture upload
        file = request.files.get("profile_picture")
        if file and allowed_file(file.filename):
            if not os.path.exists(UPLOAD_FOLDER / username):
                os.makedirs(UPLOAD_FOLDER / username, exist_ok=True)
            filename = f"user_{user_id}_" + file.filename
            file_path = UPLOAD_FOLDER / username / filename
            file.save(file_path)
            if os.path.exists(file_path):
                split_path = str(file_path).split("\\")
                file_path = '../'+"/".join(split_path[6:])
                user.profile_picture_path = file_path


        #process bio update
        new_bio = request.form.get("bio", "")
        user.bio = new_bio

        #update user in repo
        repo.update_user(user)
        return redirect(url_for("user.view_user_profile", username=user.username))
    return render_template("pages/user/settings.html", user=user)