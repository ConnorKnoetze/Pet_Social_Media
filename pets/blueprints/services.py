from pets.adapters import repository


def _repo():
    r = repository.repo_instance
    if r is None:
        raise RuntimeError("Repository not initialized")
    return r


def user_type_by_name(username: str) -> str | None:
    repo = _repo()
    user = repo.get_pet_user_by_name(username)
    if user:
        return "pet"
    return "human"
