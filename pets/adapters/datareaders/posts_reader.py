from pathlib import Path
from typing import List
import csv
from datetime import datetime

from pets.domainmodel.Comment import Comment
from pets.domainmodel.Like import Like
from pets.domainmodel.Post import Post

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "posts_table.csv"


class PostsReader:
    def __init__(self):
        self.__posts: List[Post] = []

    def read_posts(self):
        with DATA_PATH.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"DEBUG: CSV headers: {reader.fieldnames}")  # Show actual headers

            for row_num, row in enumerate(reader, start=2):  # start=2 (header is row 1)
                try:
                    if row["size"]:
                        size_tuple = tuple(map(int, row["size"].split(", ")))
                    else:
                        size_tuple = (0, 0)

                    post = Post(
                        id=int(row["id"]),
                        user_id=int(row["user_id"]),
                        caption=row["caption"],
                        views=int(row["views"]),
                        created_at=datetime.fromisoformat(
                            row["created_at"].replace("Z", "+00:00")
                        ),
                        size=size_tuple,
                        tags=row["tags"].split(","),
                        users_tagged=[],
                        media_path=Path(row["media_path"]),
                        media_type=row["media_type"],
                    )
                    self.__posts.append(post)
                except (KeyError, ValueError, TypeError) as e:
                    print(f"DEBUG: Error parsing post at row {row_num}: {e}")
                    print(f"DEBUG: Row data: {row}")
        return self.__posts

    def assign_likes(self, likes: List[Like]):
        post_dict = {post.id: post for post in self.__posts}
        for like in likes:
            if like.post_id in post_dict:
                post_dict[like.post_id].add_like(like)

    def assign_comments(self, comments: List[Comment]):
        post_dict = {post.id: post for post in self.__posts}
        for comment in comments:
            if comment.post_id in post_dict:
                post_dict[comment.post_id].add_comment(comment)

    @property
    def posts(self) -> List[Post]:
        return self.__posts
