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

feed_bp = Blueprint("feed", __name__)
BATCH_SIZE = 8


def _repo():
    r = repository.repo_instance
    if r is None:
        raise RuntimeError("Repository not initialized")
    return r


def _serialize_post(p):
    created = getattr(p, "created_at", "")
    if hasattr(created, "isoformat"):
        created = created.isoformat()
    media_path = getattr(p, "media_path", "")
    if isinstance(media_path, Path):
        media_path = str(media_path)
    # Try several attribute names for the owning user
    user_id = (
        getattr(p, "user_id", None)
        or getattr(p, "owner_id", None)
        or getattr(getattr(p, "user", None), "id", None)
        or getattr(getattr(p, "owner", None), "id", None)
        or getattr(getattr(p, "pet_user", None), "id", None)
        or 0
    )
    return {
        "id": int(getattr(p, "id", 0)),
        "user_id": int(user_id),
        "caption": str(getattr(p, "caption", "")),
        "created_at": created,
        "media_type": str(getattr(p, "media_type", "")),
        "media_path": str(media_path),
    }


@feed_bp.route("/")
@login_required
def feed():
    # Require login to view root feed

    print(session.get("user_name"))

    if not session.get("user_name"):
        return redirect(url_for("authentication_bp.register"))

    all_posts = _repo().get_photo_posts()
    all_posts.sort(key=lambda p: getattr(p, "created_at", None), reverse=True)
    initial = all_posts[:BATCH_SIZE]
    return render_template("pages/feed.html", posts=initial)


@feed_bp.route("/api/feed")
def feed_batch():
    all_posts = _repo().get_photo_posts()
    all_posts.sort(key=lambda p: getattr(p, "created_at", None), reverse=True)
    try:
        offset = int(request.args.get("offset", 0))
        if offset < 0:
            offset = 0
    except ValueError:
        offset = 0
    slice_ = all_posts[offset : offset + BATCH_SIZE]
    next_offset = offset + len(slice_)
    has_more = next_offset < len(all_posts)
    return jsonify(
        {
            "posts": [_serialize_post(p) for p in slice_],
            "offset": offset,
            "next_offset": next_offset,
            "has_more": has_more,
            "batch_size": BATCH_SIZE,
            "total": len(all_posts),
        }
    )


@feed_bp.route("/api/comments/<int:post_id>")
def comments(post_id: int):
    repo = _repo()
    try:
        items = repo.get_comments_for_post(post_id) or []
    except AttributeError:
        items = []

    def username_for(user_id: int):
        u = repo.get_human_user_by_id(user_id) or repo.get_pet_user_by_id(user_id)
        return getattr(u, "username", f"User {user_id}")

    def ser(c):
        created = getattr(c, "created_at", "")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        author = getattr(c, "author", None) or username_for(getattr(c, "user_id", 0))
        text = getattr(c, "text", None) or getattr(c, "comment_string", "")
        return {"author": str(author), "text": str(text), "created_at": created}

    return jsonify({"post_id": post_id, "comments": [ser(c) for c in items]})


@feed_bp.route("/api/user/<int:user_id>")
def user(user_id: int):
    repo = _repo()
    user = repo.get_pet_user_by_id(user_id) or repo.get_human_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    def serialize(u):
        return {
            "id": int(getattr(u, "id", 0)),
            "username": str(getattr(u, "username", "")),
            "bio": str(getattr(u, "bio", "")),
            "profile_picture_path": str(getattr(u, "profile_picture_path", "")),
            "posts_count": len(getattr(u, "posts", [])),
            "followers_count": len(getattr(u, "follower_ids", [])),
            "posts_thumbnails": repo.get_posts_thumbnails(user_id),
        }

    return jsonify(serialize(user))
