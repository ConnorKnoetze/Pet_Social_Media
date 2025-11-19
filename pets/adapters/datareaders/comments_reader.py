from pathlib import Path
from typing import List
import csv

from pets.domainmodel.Comment import Comment

DATA_PATH = Path(__file__).resolve().parent.parent/"data"/"comments_table.csv"

class CommentsReader:
    def __init__(self):
        self.__comments : List[Comment] = []

    def read_comments(self):
        with DATA_PATH.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                comment = Comment(
                    id=int(row["id"]),
                    user_id=int(row["user_id"]),
                    post_id=int(row["post_id"]),
                    created_at=row["created_at"],
                    comment_string=row["comment_string"],
                    likes=int(row["likes"]),
                )
                self.__comments.append(comment)
        return self.__comments

if __name__ == "__main__":
    reader = CommentsReader()
    comments = reader.read_comments()
    for comment in comments:
        print(comment)