from datetime import datetime
from pathlib import Path
from typing import List
import csv

from pets.domainmodel.Like import Like

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "likes_table.csv"


class LikesReader:
    def __init__(self):
        self.__likes: List[Like] = []

    def read_likes(self):
        with DATA_PATH.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                created_at_str = row["created_at"]
                # Adjust parsing to your format:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except ValueError:
                    created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                like = Like(
                    id=int(row["id"]),
                    user_id=int(row["user_id"]),
                    post_id=int(row["post_id"]),
                    created_at=created_at,
                )
                self.__likes.append(like)
        return self.__likes

    @property
    def likes(self) -> List[Like]:
        return self.__likes


if __name__ == "__main__":
    reader = LikesReader()
    likes = reader.read_likes()
    for like in likes:
        print(like)
