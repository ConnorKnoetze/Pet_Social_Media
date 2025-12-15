import os
from pathlib import Path

from flask import url_for
from werkzeug.utils import secure_filename

PROJECT_ROOT = Path(__file__).parent.parent.parent
PFP_FOLDER = PROJECT_ROOT / "static" / "images" / "uploads" / "profile_pictures"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(PFP_FOLDER):
    os.makedirs(PFP_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, user):
    """Save an uploaded file to the appropriate user directory and return its URL path."""
    if file and allowed_file(file.filename):

        ## Remove existing profile pictures for the user
        if not os.path.exists(PFP_FOLDER / user.username):
            os.makedirs(PFP_FOLDER / user.username, exist_ok=True)
        if os.listdir(PFP_FOLDER / user.username):
            for f in os.listdir(PFP_FOLDER / user.username):
                if f.startswith(f"user_{user.user_id}_"):
                    os.remove(PFP_FOLDER / user.username / f)

        user_folder = PFP_FOLDER / user.username
        user_folder.mkdir(parents=True, exist_ok=True)
        filename = f"user_{user.user_id}_" + secure_filename(file.filename)
        full_path = user_folder / filename
        file.save(full_path)
        if full_path.exists():
            static_root = PROJECT_ROOT / "static"
            rel_path = full_path.relative_to(static_root)
            user.profile_picture_path = url_for(
                "static", filename=str(rel_path).replace("\\", "/")
            )