from pets.adapters.repository import AbstractRepository
from pets.adapters.datareaders.data_reader import DataReader


def populate(repo: AbstractRepository, database_mode: bool = False):
    data_reader = DataReader()

    if database_mode:
        # Database mode: add data via repository methods
        print("populating pet users...")
        repo.add_multiple_pet_users(data_reader.users)
        print("done populating pet users")
        print("populating posts...")
        repo.add_multiple_posts(data_reader.users, data_reader.posts)
        print("done populating posts")
        print("populating comments...")
        repo.add_multiple_comments(data_reader.users, data_reader.comments)
        print("done populating comments")
        print("populating likes...")
        repo.add_multiple_likes(data_reader.likes)
        print("done populating likes")
        print("populating followers...")
        repo.add_multiple_followers([(u.user_id, u.follower_ids) for u in data_reader.users])
        print("done populating followers")
    else:
        # Memory mode: simple population
        repo.populate(data_reader.users, data_reader.max_like_id)
