from pets.adapters.repository import AbstractRepository
from pets.adapters.datareaders.data_reader import DataReader


def populate(repo: AbstractRepository, database_mode: bool = False):
    data_reader = DataReader()

    if database_mode:
        # Database mode: add data via repository methods
        repo.add_multiple_pet_users(data_reader.users)
        repo.add_multiple_posts(data_reader.users, data_reader.posts)
        repo.add_multiple_comments(data_reader.users, data_reader.comments)
        repo.add_multiple_likes(data_reader.likes)
    else:
        # Memory mode: simple population
        repo.populate(data_reader.users, data_reader.max_like_id)