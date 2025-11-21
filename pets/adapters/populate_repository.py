from pets.adapters.repository import AbstractRepository
from pets.adapters.datareaders.data_reader import DataReader


def populate(repo: AbstractRepository):
    data_reader = DataReader()
    repo.populate(data_reader.users)