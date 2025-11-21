import os
from pathlib import Path

from pets.adapters.repository import AbstractRepository
from pets.adapters.datareader.csvdatareader import CSVDataReader


def populate(repo: AbstractRepository, database_mode: bool):


    repo.add_multiple_authors(authors)
    repo.add_multiple_recipes(recipes)
    repo.add_multiple_categories(categories)
