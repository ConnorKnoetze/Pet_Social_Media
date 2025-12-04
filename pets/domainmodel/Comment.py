from datetime import datetime
from typing import List
from pets.domainmodel.Like import Like


class Comment:
    __id: int
    __user_id: int
    __post_id: int
    __created_at: datetime
    __comment_string: str
    __likes: int

    def __init__(
        self,
        id: int,
        user_id: int,
        post_id: int,
        created_at: datetime,
        comment_string: str,
        likes: int,
    ):
        self.__id = id
        self.__user_id = user_id
        self.__post_id = post_id
        self.__created_at = created_at
        self.__comment_string = comment_string
        self.__likes = likes

    def __eq__(self, other):
        if not isinstance(other, Comment):
            return False
        return (
            self.id == other.id
            and self.user_id == other.user_id
            and self.__post_id == other.__post_id
            and self.comment_string == other.comment_string
        )

    def __str__(self) -> str:
        return self.__comment_string

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def post_id(self) -> int:
        return self.__post_id

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @property
    def comment_string(self) -> str:
        return self.__comment_string

    @comment_string.setter
    def comment_string(self, value: str):
        self.__comment_string = value

    @property
    def likes(self) -> int:
        return self.__likes

    def add_like(self):
        self.__likes += 1
