# from pets.adapters.database_repository import SqlAlchemyRepository
from pets.adapters import repository
from pets.adapters.repository import AbstractRepository
from werkzeug.security import generate_password_hash, check_password_hash


from pets.domainmodel.User import User


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(
    user_name: str,
    email: str,
    password: str,
):
    repo = repository.repo_instance
    user = repo.get_pet_user_by_name(user_name)
    print(user)
    id = repo.get_total_user_size()
    if user is not None:
        raise NameNotUniqueException

    password_hash = generate_password_hash(password)
    user = User(id, user_name, email, password_hash)
    print(user, user.password_hash)
    repo.add_pet_user(user)


def get_user(user_name: str, repo: AbstractRepository):
    user = repo.get_pet_user_by_name(
        user_name
    )  # this is returning none? Meaning the database get_user function is not workign

    if user is None:
        raise UnknownUserException
    return user_to_dict(user)


def authenticate_user(user_name: str, password: str, repo: AbstractRepository):
    authenticated = False
    user = repo.get_pet_user_by_name(user_name)
    if user is not None:
        authenticated = check_password_hash(user.password_hash, password)
    if not authenticated:
        raise AuthenticationException


def get_user_by_id(user_id, repo: AbstractRepository):
    user = repo.get_pet_user_by_id(user_id)
    if user is None:
        raise UnknownUserException
    return user_to_dict(user)


def user_to_dict(user: User) -> dict:
    user_dict = {
        "user_id": str(user.id),
        "email": user.email,
        "user_name": user.username,
        "password": user.password_hash,
    }
    return user_dict
