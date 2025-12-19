"""Authentication utility functions for the recipe application."""

from flask import session
import pets.adapters.repository as repository


def get_current_user():
    """Get current user from session or return None if not logged in."""
    username = session.get("user_name")
    if not username:
        return None

    repo = repository.repo_instance
    if repo is None:
        return None

    return repo.get_pet_user_by_name(username)


def is_logged_in():
    """Check if user is currently logged in and exists in repository."""
    username = session.get("user_name")
    if not username:
        return False

    repo = repository.repo_instance
    if repo is None:
        return False

    user = (
        repo.get_pet_user_by_name(username)
        or repo.get_human_user_by_name(username)
        or repo.get_temp_user_by_name(username)
    )
    return user is not None
