from pathlib import Path
from typing import List
import csv

from pets.domainmodel.Post import Post

DATA_PATH = Path(__file__).resolve().parent.parent/"data"/"posts_table.csv"

class PostsReader:
    def __init__(self):
        self.__posts : List[Post] = []

    def read_posts(self):
        with DATA_PATH.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                post = Post(
                    id=int(row["id"]),
                    user_id=int(row["user_id"]),
                    caption=row["caption"],
                    views=int(row["views"]),
                    created_at=row["created_at"],
                    size=(int(row["width"]), int(row["height"])),
                    tags=row["tags"].split(","),
                    users_tagged=[],  # This would require additional logic to populate
                    media_path=Path(row["media_path"]),
                    media_type=row["media_type"]
                )
                self.__posts.append(post)
        return self.__posts