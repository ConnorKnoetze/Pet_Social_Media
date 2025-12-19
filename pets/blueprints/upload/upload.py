import os
import uuid
from flask import (
    Blueprint,
    render_template,
    session,
    jsonify,
    request,
)
from werkzeug.utils import secure_filename
from pets.blueprints.authentication.authentication import login_required
from pets.blueprints.services import _repo
from PIL import Image

upload_bp = Blueprint("upload", __name__)

TEMP_UPLOAD_FOLDER = "pets/static/images/uploads/temp_uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["GET"])
@login_required
def upload_page():
    username = session.get("user_name")
    repo = _repo()
    user = repo.get_pet_user_by_name(username)
    if not user:
        return "User not found", 404
    return render_template("pages/upload/upload.html", user=user)


@upload_bp.route("/api/upload/preview", methods=["POST"])
@login_required
def preview_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename_secure = secure_filename(file.filename)
    ext = filename_secure.rsplit(".", 1)[1].lower()

    user_name = session.get("user_name")
    user_temp_folder = os.path.join(TEMP_UPLOAD_FOLDER, user_name)
    os.makedirs(user_temp_folder, exist_ok=True)

    # Generate unique temp ID and path
    temp_id = str(uuid.uuid4())
    temp_filename = f"{temp_id}.{ext}"
    temp_path = os.path.join(user_temp_folder, temp_filename)

    try:
        # Process images with PIL to preserve aspect ratio and reduce size
        if ext in {"png", "jpg", "jpeg", "gif"}:
            from PIL import ImageOps

            image = Image.open(file.stream)
            image = ImageOps.exif_transpose(image)  # fix orientation from EXIF

            width, height = image.size

            # Choose UHD box based on orientation
            if width >= height:
                target = (1920, 1080)
            else:
                target = (1080, 1920)

            # Resize in-place; thumbnail preserves aspect ratio and avoids upscaling
            image.thumbnail(target, Image.LANCZOS)

            # Prepare save options to reduce file size
            save_kwargs = {}
            if ext in {"jpg", "jpeg"}:
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                save_kwargs.update({"format": "JPEG", "quality": 85, "optimize": True})
            elif ext == "png":
                save_kwargs.update({"format": "PNG", "optimize": True})
            else:
                # GIF or other: save as-is (PIL will handle)
                save_kwargs.update({})

            image.save(temp_path, **save_kwargs)
        else:
            # For videos or other allowed types, just save the uploaded file
            file.save(temp_path)
    except Exception as e:
        return jsonify({"error": "Could not process file", "details": str(e)}), 500

    return jsonify(
        {
            "temp_id": temp_id,
            "url": f"/static/images/uploads/temp_uploads/{user_name}/{temp_filename}",
            "type": file.content_type,
        }
    )


@upload_bp.route("/api/upload/finalize", methods=["POST"])
@login_required
def finalize_upload():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    temp_id = data.get("temp_id")
    caption = data.get("caption", "")
    tags = data.get("tags", "")
    url = data.get("url")

    user_name = session.get("user_name")
    if not url or f"/{user_name}/" not in url or "temp_uploads" not in url:
        return jsonify({"error": "Invalid or unauthorized url"}), 400

    filename = url.rsplit("/", 1)[-1]
    temp_path = os.path.join(
        "pets", "static", "images", "uploads", "temp_uploads", user_name, filename
    )

    if not os.path.exists(temp_path):
        return jsonify({"error": "File not found"}), 404

    dest_dir = os.path.join("pets", "static", "images", "uploads", user_name)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)

    try:
        import shutil

        shutil.move(temp_path, dest_path)
    except Exception as e:
        return jsonify({"error": "Could not move file", "details": str(e)}), 500

    # Remove the user's temp uploads directory
    temp_user_dir = os.path.join(
        "pets", "static", "images", "uploads", "temp_uploads", user_name
    )
    temp_removed = False
    temp_remove_error = None
    try:
        # Safety check to avoid accidental deletes
        expected_prefix = os.path.join("pets", "static", "images", "uploads")
        expected_suffix = os.path.join("temp_uploads", user_name)
        if (
            temp_user_dir.startswith(expected_prefix)
            and temp_user_dir.endswith(expected_suffix)
            and os.path.isdir(temp_user_dir)
        ):
            shutil.rmtree(temp_user_dir)
            temp_removed = True
    except Exception as e:
        temp_remove_error = str(e)

    user = _repo().get_pet_user_by_name(user_name)
    if not user:
        return jsonify({"error": "User not found"}), 404

    media_path = os.path.join("static", "images", "uploads", user_name, filename)

    post = _repo().create_post(
        user=user,
        caption=caption,
        tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
        media_path=media_path,
        media_type="photo"
        if filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}
        else "video",
    )

    _repo().add_post(user, post)

    resp = {
        "success": True,
        "message": "Upload completed",
        "url": f"/static/images/uploads/{user_name}/{filename}",
        "temp_removed": temp_removed,
    }
    if temp_remove_error:
        resp["temp_remove_error"] = temp_remove_error

    return jsonify(resp)
