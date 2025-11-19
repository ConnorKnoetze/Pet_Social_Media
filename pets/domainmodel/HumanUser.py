from pets.domainmodel.User import User
from pets.domainmodel.Post import Post
from pets.domainmodel.Comment import Comment
from pets.domainmodel.AnimalType import AnimalType

from typing import List
from pathlib import Path
from datetime import datetime


class HumanUser(User):
    __favourite_animals: List[AnimalType]
    __friends: List[User]

    def __init__(
        self,
        id : int,
        username: str,
        email: str,
        password_hash: str,
        profile_picture_path: Path,
        created_at: datetime,
        liked_posts: List[Post] = None,
        following: List[User] = None,
        comments: List[Comment] = None,
        bio: str = "",
        favourite_animals: List[AnimalType] = None,
        friends: List[User] = None,
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
        self.__favourite_animals: List[AnimalType] = (
            favourite_animals if favourite_animals is not None else []
        )
        self.__friends: List[User] = [] if friends is not None else []

    @property
    def favourite_animals(self) -> List[AnimalType]:
        return self.__favourite_animals

    def add_favourite_animal(self, animal: AnimalType):
        if animal not in self.__favourite_animals and isinstance(animal, AnimalType):
            self.__favourite_animals.append(animal)

    def remove_favourite_animal(self, animal: AnimalType):
        if animal in self.__favourite_animals and isinstance(animal, AnimalType):
            self.__favourite_animals.remove(animal)

    @property
    def friends(self) -> List[User]:
        return self.__friends

    def add_friend(self, friend: User):
        if friend not in self.__friends and isinstance(friend, User):
            self.__friends.append(friend)

    def remove_friend(self, friend: User):
        if friend in self.__friends and isinstance(friend, User):
            self.__friends.remove(friend)
