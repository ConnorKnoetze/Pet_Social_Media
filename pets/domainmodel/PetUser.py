from overrides import overrides

from pets.domainmodel.User import User
from pets.domainmodel.Post import Post
from pets.domainmodel.Comment import Comment
from pets.domainmodel.AnimalType import AnimalType

from typing import List, Optional
from pathlib import Path
from datetime import datetime


class PetUser(User):
    __posts: List[Post]
    __animal_type: AnimalType
    __follower_ids: List[int]

    def __init__(
        self,
        user_id: int = None,
        username: str = "",
        email: str = "",
        password_hash: str = "",
        profile_picture_path: Path | None = None,
        created_at: datetime | None = None,
        liked_posts: List[Post] = None,
        following: List[User] = None,
        comments: List[Comment] = None,
        bio: str = "",
        posts: List[Post] = None,
        animal_type: AnimalType = None,
        follower_ids: List[int] = None,
    ):
        # allow created_at to default to now if not provided
        if created_at is None:
            created_at = datetime.now()

        super().__init__(
            user_id,
            username,
            email,
            password_hash,
            profile_picture_path,
            created_at,
            liked_posts,
            following,
            comments,
            bio,
        )
        self.__posts: List[Post] = posts if posts is not None else []
        self.__animal_type: AnimalType = animal_type
        self.__follower_ids: List[int] = (
            follower_ids if follower_ids is not None else []
        )

    @overrides
    def __str__(self):
        return f"PetUser({self.user_id}, {self.username}, {self.email}, {self.animal_type}, Posts: {len(self.posts)}, Followers: {len(self.follower_ids)})"

    @property
    def posts(self) -> List[Post]:
        return self.__posts

    @property
    def animal_type(self) -> AnimalType:
        return self.__animal_type

    @property
    def follower_ids(self) -> List[int]:
        return self.__follower_ids

    def add_post(self, post: Post):
        if post not in self.__posts and isinstance(post, Post):
            self.__posts.append(post)

    def delete_post(self, post: Post):
        if post in self.__posts and isinstance(post, Post):
            self.__posts.remove(post)

    def add_follower(self, user_id: int):
        print(user_id)
        if isinstance(user_id, int) and user_id not in self.__follower_ids:
            self.__follower_ids.append(user_id)
        print(self.__follower_ids)

    def remove_follower(self, user_id: int):
        if user_id in self.__follower_ids:
            self.__follower_ids.remove(user_id)