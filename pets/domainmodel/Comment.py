from datetime import datetime
from typing import List
from pets.domainmodel.Like import Like


class Comment:
    __id: int
    __user_id: int
    __post_id: int
    __created_at: datetime
    __comment_string: str
    __likes: List[Like]

    def __init__(
        self,
        id: int,
        user_id: int,
        created_at: datetime,
        comment_string: str,
        likes: List[Like],
    ):
        self.__id = id
        self.__user_id = user_id
        self.__created_at = created_at
        self.__comment_string = comment_string
        self.__likes = likes

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user_id(self) -> int:
        return self.__user_id

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
    def likes(self) -> List[Like]:
        return self.__likes

    def add_like(self, like: Like):
        self.__likes.append(like)
