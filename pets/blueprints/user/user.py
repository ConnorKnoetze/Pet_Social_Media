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
from pets.blueprints.authentication.authentication import login_required
from pets.blueprints.services import _repo

from pets.blueprints.user.services import save_file

user_bp = Blueprint("user", __name__)


@user_bp.route("/user/<string:username>")
@login_required
def view_user_profile(username: str):
    repo = _repo()
    user = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(username)
    if not user:
        return "User not found", 404
    if "." == str(user.profile_picture_path):
        user.profile_picture_path = Path('../static/images/assets/user.png')
    # Adjusted template path to match actual location under pages/
    posts = [post for post in user.posts if post.media_type == "photo"]
    posts.sort(key=lambda p: p.created_at, reverse=True)

    ## Temporary fix for media path issues move to standard service when only database used
    post_paths = [os.path.join("../", post.media_path) if user.username in str(post.media_path) and "uploads" in str(post.media_path) else post.media_path for post in posts]
    post_path_tuples = [(posts[i], post_paths[i]) for i in range(len(posts))]

    return render_template("pages/user/profile.html", user=user, posts=posts, image_path=user.profile_picture_path, post_path_tuples=post_path_tuples)

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

        print(user.profile_picture_path)

        # process profile picture upload
        file = request.files.get("profile_picture")
        save_file(file, user)

        print(user.profile_picture_path)

        #process bio update
        new_bio = request.form.get("bio", "")
        if len(new_bio) > 255:
            return "Bio must be 255 characters or less", 400
        user.bio = new_bio

        #update user in repo
        repo.update_user(user)
        return redirect(url_for("user.view_user_profile", username=user.username))

    username = (user.username[0].upper() if user.username[0].isalpha() else user.username[0]) + user.username[1:]
    return render_template("pages/user/settings.html", user=user, username=username)

@user_bp.route("/user/<string:username>/followers")
@login_required
def view_followers(username: str):
    repo = _repo()
    user = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(username)
    if not user:
        return "User not found", 404
    followers = repo.get_followers(user)
    return render_template("pages/user/followers.html", user=user, followers=followers)