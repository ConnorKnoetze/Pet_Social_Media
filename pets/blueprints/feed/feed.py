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


@feed_bp.route("/api/posts/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id: int):
    repo = _repo()
    username = session.get("user_name")
    if not username:
        return jsonify({"error": "Not authenticated"}), 401

    user = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(username)
    if not user:
        return jsonify({"error": "User not found"}), 403

    post = repo.get_post_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    user_id = getattr(user, "id", None)
    likes_list = getattr(post, "likes", []) or []
    existing = next(
        (l for l in likes_list if getattr(l, "user_id", None) == user_id), None
    )

    if existing:
        # user already liked -> remove (toggle off)
        repo.delete_like(user, post)
        liked = False
    else:
        # not liked -> add (toggle on)

        repo.add_like(user, post)
        liked = True

    likes_count = len(getattr(post, "likes", []) or [])
    return (
        jsonify(
            {
                "post_id": post_id,
                "liked": liked,
                "already_liked": existing is not None,
                "likes_count": likes_count,
            }
        ),
        200,
    )


@feed_bp.route("/")
@login_required
def feed():
    # Require login to view root feed

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


@feed_bp.route("/api/post/<int:post_id>/comment/<int:comment_id>", methods=["POST"])
@login_required
def add_like_to_comment(post_id: int, comment_id: int):
    repo = _repo()
    username = session.get("user_name")
    if not username:
        return jsonify({"error": "Not authenticated"}), 401

    comments = repo.get_comments_for_post(post_id)
    comment = next((c for c in comments if getattr(c, "id", None) == comment_id), None)

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    repo.add_like_to_comment(comment)
    return jsonify(
        {
            "message": "Like added to comment",
            "post_id": post_id,
            "comment_id": comment_id,
            "likes": getattr(comment, "likes", 0),
        }
    ), 200


@feed_bp.route("/api/comments/<int:post_id>", methods=["GET", "POST"])
def comments(post_id: int):
    repo = _repo()
    if request.method == "POST":
        # Require authenticated user
        username = session.get("user_name")
        if not username:
            return jsonify({"error": "Not authenticated"}), 401
        user = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(
            username
        )
        if not user:
            return jsonify({"error": "User not found"}), 403
        post = repo.get_post_by_id(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Empty comment"}), 400
        if len(text) > 500:
            return jsonify({"error": "Comment too long"}), 400
        comment = repo.create_comment(user, post, text)
        created = getattr(comment, "created_at", "")
        if hasattr(created, "isoformat"):
            created = created.isoformat()

        pfp=getattr(user, "profile_picture_path", "")
        if "." == str(pfp):
            pfp = Path('/static/images/assets/user.png')

        return (
            jsonify(
                {
                    "post_id": post_id,
                    "comment": {
                        "id": int(getattr(comment, "id", 0)),
                        "author": getattr(user, "username", ""),
                        "user_id": getattr(user, "id", 0),
                        "text": text,
                        "created_at": created,
                        "profile_picture_path": str(pfp),
                        "likes": 0,
                    },
                }
            ),
            201,
        )

    # GET branch
    post = repo.get_post_by_id(post_id)
    items = []
    if post is not None:
        items = list(getattr(post, "comments", []) or [])

    def user_for(user_id: int):
        return repo.get_human_user_by_id(user_id) or repo.get_pet_user_by_id(user_id)

    def username_for(user_id: int):
        u = user_for(user_id)
        return getattr(u, "username", f"User {user_id}")

    def ser(c):
        created = getattr(c, "created_at", "")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        uid = getattr(c, "user_id", 0)
        u = user_for(uid)
        pfp=getattr(u, "profile_picture_path", "")
        if not '.' == str(pfp):
            pfp = Path('/static/images/assets/user.png')

        author = getattr(c, "author", None) or username_for(uid)
        text = getattr(c, "text", None) or getattr(c, "comment_string", "")
        likes = getattr(c, "likes", 0)
        # include id so client can post likes for specific comment
        return {
            "id": int(getattr(c, "id", 0)),
            "author": str(author),
            "user_id": int(uid),
            "text": str(text),
            "created_at": created,
            "profile_picture_path": str(pfp),
            "likes": int(likes),
        }

    return jsonify({"post_id": post_id, "comments": [ser(c) for c in items]})


@feed_bp.route("/api/user/<int:user_id>")
def user(user_id: int):
    session_user = session.get("user_name")
    if session_user:
        repo = _repo()
        session_user = repo.get_human_user_by_name(
            session_user
        ) or repo.get_pet_user_by_name(session_user)
    else:
        session_user = None
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
            "followers_count": len(repo.get_followers(u)),
            "posts_thumbnails": repo.get_posts_thumbnails(user_id),
            "following": repo.is_following(session_user.user_id, user.user_id),
            "session_user_id": session_user.user_id if session_user else None,
        }

    return jsonify(serialize(user))


@feed_bp.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow_user(user_id: int):
    repo = _repo()
    username = session.get("user_name")
    if not username:
        return jsonify({"error": "Not authenticated"}), 401

    follower = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(
        username
    )
    if not follower:
        return jsonify({"error": "User not found"}), 403

    followee = repo.get_pet_user_by_id(user_id) or repo.get_human_user_by_id(user_id)
    if not followee:
        return jsonify({"error": "User to follow not found"}), 404

    if followee.user_id == follower.user_id:
        return jsonify({"error": "Cannot follow yourself"}), 400

    repo.follow_user(follower, followee)

    return jsonify(
        {
            "message": f"You are now following {followee.username}",
            "user_id": followee.user_id,
            "followers_count": len(repo.get_followers(followee)),
        }
    ), 200

@feed_bp.route("/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow_user(user_id: int):
    repo = _repo()
    username = session.get("user_name")
    if not username:
        return jsonify({"error": "Not authenticated"}), 401

    follower = repo.get_human_user_by_name(username) or repo.get_pet_user_by_name(
        username
    )
    if not follower:
        return jsonify({"error": "User not found"}), 403

    followee = repo.get_pet_user_by_id(user_id) or repo.get_human_user_by_id(user_id)
    if not followee:
        return jsonify({"error": "User to unfollow not found"}), 404

    if followee.user_id == follower.user_id:
        return jsonify({"error": "Cannot unfollow yourself"}), 400

    repo.unfollow_user(follower, followee)

    return jsonify(
        {
            "message": f"You have unfollowed {followee.username}",
            "user_id": followee.user_id,
            "followers_count": len(repo.get_followers(followee)),
        }
    ), 200