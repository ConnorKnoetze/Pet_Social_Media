from pathlib import Path
from typing import List
import csv

from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.Post import Post

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pet_user_table.csv"


class PetUserReader:
    def __init__(self):
        self.__users: List[PetUser] = []

    def read_pet_users(self):
        with DATA_PATH.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                follower_ids = row["follower_ids"].split(",")
                int_ids = [int(id) for id in follower_ids]
                user = PetUser(
                    id=int(row["id"]),
                    username=row["username"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    profile_picture_path=Path(row["profile_image_path"]),
                    created_at=row["created_at"],
                    bio=row["bio"],
                    follower_ids=int_ids,
                )
                print(user.follower_ids)
                self.__users.append(user)
        return self.__users

    def assign_posts(self, posts: List[Post]):
        user_dict = {user.id: user for user in self.__users}
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
