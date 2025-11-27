import abc
from typing import List
from datetime import date


from pets.domainmodel import PetUser, HumanUser, User, Like, Comment, Post

repo_instance = None


class RepositoryException(Exception):
    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add_pet_user(self, user: User):
        # Adds a User to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_pet_users(self, users: List[User]):
        # Adds multiple Users to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def add_human_user(self, user: User):
        # Adds a User to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_human_users(self, users: List[User]):
        # Adds multiple Users to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def get_human_user_by_name(self, username) -> User:
        # Retrieves a User by their username.
        raise NotImplementedError

    @abc.abstractmethod
    def get_pet_user_by_name(self, username) -> User:
        # Retrieves a User by their username.
        raise NotImplementedError

    @abc.abstractmethod
    def get_human_user_by_id(self, id: int) -> User:
        # Retrieves a User by their ID.
        raise NotImplementedError

    @abc.abstractmethod
    def get_pet_user_by_id(self, id: int) -> User:
        # Retrieves a User by their ID.
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_user_post_paths(self, user: User) -> List[str]:
        # Retrieves all post media paths for a given user.
        raise NotImplementedError

    @abc.abstractmethod
    def get_pet_users(self) -> List[User]:
        # Retrieves all pet users.
        raise NotImplementedError

    @abc.abstractmethod
    def get_human_users(self) -> List[User]:
        # Retrieves all human users.
        raise NotImplementedError

    @abc.abstractmethod
    def add_post(self, user: User, post: Post):
        # Adds a Post to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def get_photo_posts(self) -> List[Post]:
        # Retrieves all photo Posts.
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_posts(self, user: User, posts: List[Post]):
        # Adds multiple Posts to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def delete_post(self, user: User, post: Post):
        # Deletes a Post from the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def get_post_by_id(self, id: int) -> Post:
        # Retrieves a Post by its ID.
        raise NotImplementedError

    @abc.abstractmethod
    def add_comment(self, user: User, comment: Comment):
        # Adds a Comment to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def get_comments_by_post(self, post: Post) -> List[Comment]:
        # Retrieves Comments for a given Post.
        raise NotImplementedError

    @abc.abstractmethod
    def get_comments_for_post(self, post_id: int) -> List[Comment]:
        # Retrieves Comments for a given Post by post ID.
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_comments(self, user: User, comments: List[Comment]):
        # Adds multiple Comments to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def add_like(self, user: User, like: Like):
        # Adds a Like to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def add_multiple_likes(self, posts: List[Post], users: List[User]):
        # Adds multiple Likes to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def delete_comment(self, user: User, comment: Comment):
        # Deletes a Comment from the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def get_posts_thumbnails(self, user_id: int) -> List[dict]:
        # Retrieves post thumbnails for a given user ID.
        raise NotImplementedError
