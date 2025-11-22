from pathlib import Path
from flask import Blueprint, render_template, jsonify, request
from pets.adapters import repository

feed_bp = Blueprint("feed", __name__)

BATCH_SIZE = 16


def _repo():
    r = repository.repo_instance
    if r is None:
        raise RuntimeError("Repository not initialized")
    return r


@feed_bp.route("/")
def feed():
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

    def serialize(p):
        created = getattr(p, "created_at", "")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        media_path = getattr(p, "media_path", "")
        if isinstance(media_path, Path):
            media_path = str(media_path)
        return {
            "id": int(getattr(p, "id", 0)),
            "caption": str(getattr(p, "caption", "")),
            "created_at": created,
            "media_type": str(getattr(p, "media_type", "")),
            "media_path": str(media_path),
        }

    return jsonify(
        {
            "posts": [serialize(p) for p in slice_],
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
        print(f"[comments] repository lacks get_comments_for_post")
        items = []

    # Optional username resolution
    def username_for(user_id: int):
        u = repo.get_human_user_by_id(user_id) or repo.get_pet_user_by_id(user_id)
        return getattr(u, "username", f"User {user_id}")

    def ser(c):
        created = getattr(c, "created_at", "")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        author = getattr(c, "author", None)
        if not author:
            author = username_for(getattr(c, "user_id", 0))
        text = getattr(c, "text", None)
        if text is None:
            text = getattr(c, "comment_string", "")
        return {"author": str(author), "text": str(text), "created_at": created}

    return jsonify({"post_id": post_id, "comments": [ser(c) for c in items]})
