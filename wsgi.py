"""App entry point."""
import os

from pets import create_app
from dotenv import load_dotenv
from pets.utilities.create_backgrounds import create_backgrounds

app = create_app()

if __name__ == "__main__":
    load_dotenv()
    if not os.path.exists("pets/static/images/backgrounds/dark") or not os.path.exists("pets/static/images/backgrounds/light"):
        print("Creating background images...")
        create_backgrounds()
    else:
        print("Background images found")

    app.run(host="0.0.0.0", port=5000, threaded=True)
