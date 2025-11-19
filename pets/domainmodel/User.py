from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from pathlib import Path
from datetime import datetime


if TYPE_CHECKING:
    from pets.domainmodel.Comment import Comment
    from pets.domainmodel.Post import Post

class User:
    __id : int
    __username: str
    __email: str
    __password_hash: str
    __profile_picture_path: Path
    __created_at: datetime
    __liked_posts: List["Post"]
    __following: List["User"]
    __comments: List["Comment"]
    __bio: str

    def __init__(
        self,
        id : int,
        username: str,
        email: str,
        password_hash: str,
        profile_picture_path: Path,
        created_at: datetime,
        liked_posts: List["Post"] = None,
        following: List["User"] = None,
        comments: List["Comment"] = None,
        bio: str = "",
    ):
        self.__id = id
        self.__username: str = username
        self.__email: str = email
        self.__password_hash: str = password_hash
        self.__profile_picture_path: Optional[Path] = (
            profile_picture_path if profile_picture_path is not None else Path("")
        )
        self.__created_at: datetime = created_at
        self.__liked_posts: List[Post] = liked_posts if liked_posts is not None else []
        self.__following: List[User] = following if following is not None else []
        self.__comments: List[Comment] = comments if comments is not None else []
        self.__bio: str = bio

    @property
    def id(self) -> int:
        return self.__id

    @property
    def username(self) -> str:
        return self.__username

    @username.setter
    def username(self, value: str):
        self.__username = value

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str):
        self.__email = value

    @property
    def password_hash(self) -> str:
        return self.__password_hash

    @password_hash.setter
    def password_hash(self, value: str):
        self.__password_hash = value

    @property
    def profile_picture_path(self) -> Path:
        return self.__profile_picture_path

    @profile_picture_path.setter
    def profile_picture_path(self, value: Path):
        self.__profile_picture_path = value

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @property
    def liked_posts(self) -> List[Post]:
        return self.__liked_posts

    def like_post(self, post: Post):
        if post not in self.__liked_posts:
            self.__liked_posts.append(post)

    @property
    def following(self) -> List[User]:
        return self.__following

    def follow(self, user: User):
        if user not in self.__following:
            self.__following.append(user)

    @property
    def comments(self) -> List[Comment]:
        return self.__comments

    def add_comment(self, comment: Comment):
        self.__comments.append(comment)

    @property
    def bio(self) -> str:
        return self.__bio

    @bio.setter
    def bio(self, value: str):
        self.__bio = value
