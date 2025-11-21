from pathlib import Path
from flask import Blueprint, render_template, jsonify, request
from pets.adapters import repository

feed_bp = Blueprint('feed', __name__)

BATCH_SIZE = 16

def _repo():
    r = repository.repo_instance
    if r is None:
        raise RuntimeError("Repository not initialized")
    return r

@feed_bp.route('/')
def feed():
    all_posts = _repo().get_photo_posts()
    all_posts.sort(key=lambda p: getattr(p, 'created_at', None), reverse=True)
    initial = all_posts[:BATCH_SIZE]
    return render_template('pages/feed.html', posts=initial)

@feed_bp.route('/api/feed')
def feed_batch():
    all_posts = _repo().get_photo_posts()
    all_posts.sort(key=lambda p: getattr(p, 'created_at', None), reverse=True)
    try:
        offset = int(request.args.get('offset', 0))
        if offset < 0:
            offset = 0
    except ValueError:
        offset = 0

    slice_ = all_posts[offset:offset + BATCH_SIZE]
    next_offset = offset + len(slice_)
    has_more = next_offset < len(all_posts)

    def serialize(p):
        created = getattr(p, "created_at", "")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        else:
            created = str(created)

        media_path = getattr(p, "media_path", "")
        # WindowsPath or other Path -> str
        if isinstance(media_path, Path):
            media_path = str(media_path)
        else:
            media_path = str(media_path)

        return {
            "id": int(getattr(p, "id", 0)),
            "caption": str(getattr(p, "caption", "")),
            "created_at": created,
            "media_type": str(getattr(p, "media_type", "")),
            "media_path": media_path
        }

    return jsonify({
        "posts": [serialize(p) for p in slice_],
        "offset": offset,
        "next_offset": next_offset,
        "has_more": has_more,
        "batch_size": BATCH_SIZE,
        "total": len(all_posts)
    })