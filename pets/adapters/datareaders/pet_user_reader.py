from datetime import datetime
from pathlib import Path
from typing import List
import csv

from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.AnimalType import AnimalType
from pets.domainmodel.Post import Post

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pet_user_table.csv"


class PetUserReader:
    def __init__(self):
        self.__users: List[PetUser] = []

    def read_pet_users(self):
        with DATA_PATH.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                created_at_str = row["created_at"].strip()
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except ValueError:
                    created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")

                # Parse follower_ids from CSV string
                follower_ids_str = row.get("follower_ids", "").strip()
                follower_ids = (
                    [int(x) for x in follower_ids_str.split(",") if x.strip()]
                    if follower_ids_str
                    else []
                )

                user = PetUser(
                    user_id=int(row["id"]),
                    username=row["username"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    profile_picture_path=row.get(
                        "profile_image_path"
                    ),  # Match your CSV column name
                    created_at=created_at,
                    bio=row.get("bio", ""),
                    animal_type=AnimalType.DOG,  # Default or read from CSV if available
                    follower_ids=follower_ids,
                )
                self.__users.append(user)
        print([str(user) for user in self.__users])
        return self.__users
    def assign_posts(self, posts: List[Post]):
        user_dict = {user.user_id: user for user in self.__users}
        for post in posts:
            if post.user_id in user_dict:
                user_dict[post.user_id].add_post(post)

    @property
    def users(self) -> List[PetUser]:
        return self.__users


if __name__ == "__main__":
    reader = PetUserReader()
    users = reader.read_pet_users()
    for user in users:
        print(user)
