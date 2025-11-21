import os
from pathlib import Path

from pets.adapters.repository import AbstractRepository
from pets.adapters.datareader.csvdatareader import CSVDataReader


def populate(data_path: Path, repo: AbstractRepository, database_mode: bool):
    # getting the absolute path
    dir_name = os.path.abspath(data_path)

    if os.path.isdir(dir_name):
        recipe_filename = os.path.join(dir_name, "recipes.csv")
    else:
        raise FileNotFoundError(f"Invalid data path: {dir_name}")

    reader = CSVDataReader(recipe_filename)
    reader.read_csv()  # when we call this function we are reading the recipe.csv file and then we have functions that we can access in which we are already doing in the memory repo, We can keep the memory repo functions and now I just need to figure out how I can populate the database which is what im going to do by using methods in teh database repository that i will write methods for

    authors = reader.sort_authors()  # authors is a list of the authors in a sorted list
    recipes = reader.sort_recipes()  # recipes is a list of the recipes in a sorted list
    categories = (
        reader.sort_categories()
    )  # categories is a list of the categories in a sorted list

    # this is populating our database or memory repo depending on the repo we are passed from the __init__
    repo.add_multiple_authors(authors)
    repo.add_multiple_recipes(recipes)
    repo.add_multiple_categories(categories)
