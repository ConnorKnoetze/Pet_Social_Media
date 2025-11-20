import abc
from typing import List
from datetime import date

repo_instance = None


class RepositoryException(Exception):
    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_animal_user(self, user: User):
        # Adds a User to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def add_human_user(self, user: User):
        # Adds a User to the repository.
        raise NotImplementedError

    @abc.abstractmethod
    def get_human_user_by_name(self, username) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_animal_user_by_name(self, username) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_human_user_by_id(self, id: int) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_animal_user_by_id(self, id: int) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_animal_users(self) -> List[User]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_human_users(self) -> List[User]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_post(self, post: Post):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_post(self, post: Post):
        raise NotImplementedError

    @abc.abstractmethod
    def get_post_by_id(self, id: int) -> Post:
        raise NotImplementedError

    @abc.abstractmethod
    def add_comment(self, comment: Comment):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_comment(self, comment: Comment):
        raise NotImplementedError


