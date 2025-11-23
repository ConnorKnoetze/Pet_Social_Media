from pets.domainmodel.User import User
from pets.domainmodel.Post import Post
from pets.domainmodel.Comment import Comment
from pets.domainmodel.AnimalType import AnimalType

from typing import List
from pathlib import Path
from datetime import datetime


class PetUser(User):
    __posts: List[Post]
    __animal_type: AnimalType
    __followers: List[User]

    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        password_hash: str,
        profile_picture_path: Path,
        created_at: datetime,
        liked_posts: List[Post] = None,
        following: List[User] = None,
        comments: List[Comment] = None,
        bio: str = "",
        posts: List[Post] = None,
        animal_type: AnimalType = None,
        followers: List[User] = None,
        follower_ids: List[int] = None,
    ):
        super().__init__(
            id,
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
        self.__followers: List[User] = followers if followers is not None else []
        self.__follower_ids = follower_ids if follower_ids is not None else []

    @property
    def posts(self) -> List[Post]:
        return self.__posts

    @property
    def animal_type(self) -> AnimalType:
        return self.__animal_type

    @property
    def followers(self) -> List[User]:
        return self.__followers

    @property
    def follower_ids(self) -> List[int]:
        return self.__follower_ids

    def add_post(self, post: Post):
        if post not in self.__posts and isinstance(post, Post):
            self.__posts.append(post)

    def delete_post(self, post: Post):
        if post in self.__posts and isinstance(post, Post):
            self.__posts.remove(post)

    def add_follower(self, user: User):
        if user not in self.__followers and isinstance(user, User):
            self.__follower_ids.append(user.id)
            self.__followers.append(user)

    def remove_follower(self, user: User):
        if user in self.__followers and isinstance(user, User):
            self.__follower_ids.remove(user.id)
            self.__followers.remove(user)
