from datetime import datetime
from pathlib import Path
from typing import List, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from pets.domainmodel.Comment import Comment
    from pets.domainmodel.Like import Like
    from pets.domainmodel.User import User


class Post:
    __id: int
    __user_id: int
    __likes: List["Like"]
    __comments: List["Comment"]
    __caption: str
    __views: int
    __created_at: datetime
    __size: Tuple[int, int]
    __tags: List[str]
    __users_tagged: List["User"]
    __media_path: Path
    __media_type: str

    def __init__(
        self,
        id: int,
        user_id: int,
        caption: str,
        views: int,
        created_at: datetime,
        size: Tuple[int, int],
        tags: List[str],
        users_tagged: List["User"],
        media_path: Path,
        media_type: str,
        comments: List["Comment"] = None,
        likes: List["Like"] = None,
    ):
        self.__id = id
        self.__user_id = user_id
        self.__likes = likes if likes is not None else []
        self.__comments = comments if comments is not None else []
        self.__caption = caption
        self.__views = views
        self.__created_at = created_at
        self.__size = size
        self.__tags = tags
        self.__users_tagged = users_tagged
        self.__media_path = media_path
        self.__media_type = media_type

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def likes(self) -> List["Like"]:
        return self.__likes

    @property
    def comments(self) -> List["Comment"]:
        return self.__comments

    @property
    def caption(self) -> str:
        return self.__caption

    @property
    def views(self) -> int:
        return self.__views

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @property
    def size(self) -> Tuple[int, int]:
        return self.__size

    @property
    def tags(self) -> List[str]:
        return self.__tags

    @property
    def users_tagged(self) -> List["User"]:
        return self.__users_tagged

    @property
    def media_path(self) -> Path:
        return self.__media_path

    @property
    def media_type(self) -> str:
        return self.__media_type

    def add_like(self, like: "Like"):
        if like not in self.__likes:
            self.__likes.append(like)

    def remove_like(self, like: "Like"):
        if like in self.__likes:
            self.__likes.remove(like)

    def add_comment(self, comment: "Comment"):
        if comment not in self.__comments:
            self.__comments.append(comment)

    def remove_comment(self, comment: "Comment"):
        if comment in self.__comments:
            self.__comments.remove(comment)

    def increment_views(self):
        self.__views += 1

    def add_tag(self, tag: str):
        if tag not in self.__tags:
            self.__tags.append(tag)

    def remove_tag(self, tag: str):
        if tag in self.__tags:
            self.__tags.remove(tag)

    def tag_user(self, user: "User"):
        if user not in self.__users_tagged:
            self.__users_tagged.append(user)

    def untag_user(self, user: "User"):
        if user in self.__users_tagged:
            self.__users_tagged.remove(user)
