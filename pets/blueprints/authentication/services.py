from datetime import datetime

from pets.adapters import repository
from pets.adapters.repository import AbstractRepository
from werkzeug.security import generate_password_hash, check_password_hash

from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.User import User


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(user_name: str, email: str, password: str):
    repo = repository.repo_instance

    if repo is None:
        raise RuntimeError(
            "repository.repo_instance is not set. Make sure the repository is initialised."
        )

    if not user_name or not isinstance(user_name, str) or user_name.strip() == "":
        raise ValueError("username is required")

    username_clean = user_name.strip()
    existing = repo.get_pet_user_by_name(username_clean)

    if existing is not None:
        raise NameNotUniqueException

    if not password:
        raise ValueError("password is required")

    password_hash = generate_password_hash(password)

    new_user = PetUser(
        username=username_clean,
        email=email,
        password_hash=password_hash,
        profile_picture_path=None,
        created_at=datetime.now(),
    )

    repo.add_pet_user(new_user)
    return new_user


def get_user(user_name: str, repo: AbstractRepository):
    user = repo.get_pet_user_by_name(user_name)

    if user is None:
        print(
            f"DEBUG: get_user - no user for '{user_name}' (repo: {repo.__class__.__name__})"
        )
        raise UnknownUserException
    return user_to_dict(user)


def authenticate_user(user_name: str, password: str, repo: AbstractRepository):
    authenticated = False
    user = repo.get_pet_user_by_name(user_name)
    if user is None:
        print(
            f"DEBUG: authenticate_user - no user for '{user_name}' (repo: {repo.__class__.__name__})"
        )
    else:
        print(
            f"DEBUG: authenticate_user - found user id={getattr(user, 'id', None)} username={getattr(user, 'username', None)}"
        )
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
        "user_id": str(user.user_id),
        "email": user.email,
        "user_name": user.username,
        "password": user.password_hash,
    }
    return user_dict
